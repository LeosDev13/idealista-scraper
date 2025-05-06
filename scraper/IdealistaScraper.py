import asyncio
import json
import random
import re
import time

from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession

from constants.constants import BASE_URL
from core.Database import Database
from core.Logger import Logger
from core.models.Money import Money
from core.models.Property import Property


class IdealistaScraper:
    def __init__(self, database: Database, logger: Logger):
        self.database = database
        self.semaphore = asyncio.Semaphore(3)
        self.session = None
        self.logger = logger

    async def get_property_data(self, session, property_url: str) -> Property | None:
        details = await self._fetch_property_details(session, property_url)
        if details:
            return Property(**details)

        self.logger.debug(f"❌ No details found for property: {property_url}")
        return None

    async def _fetch_property_details(self, session, property_url):
        async with self.semaphore:
            try:
                response = await session.get(f"{BASE_URL}{property_url}")
                response.raise_for_status()
            except Exception as e:
                self.logger.error(f"Failed to fetch {property_url}: {e}")
                return None

            soup = BeautifulSoup(response.text, "lxml")
            await asyncio.sleep(random.uniform(5, 15))

            return self._extract_property_details(soup, property_url)

    def _extract_property_details(
        self, soup: BeautifulSoup, property_url: str
    ) -> dict | None:
        json_data = self._extract_utag_data(soup)
        if not json_data:
            return None

        return {
            **self._extract_characteristics(json_data),
            **self._extract_condition(json_data),
            "price": Money(amount=self._extract_price(json_data), currency="EUR"),
            "agency_name": self._extract_agency_name(json_data),
            **self._extract_metadata(soup, property_url),
            "is_illegally_occupied": self._extract_is_illegally_occupied(soup),
            "id": self._extract_id(json_data),
        }

    def _extract_id(self, data: dict) -> str:
        return data.get("ad", {}).get("id", "")

    def _extract_utag_data(self, soup: BeautifulSoup) -> dict | None:
        regex = re.compile(r"var\s*utag_data\s*=\s*(\{.*?\});", re.DOTALL)
        script_text = regex.search(soup.prettify())
        if not script_text:
            self.logger.error("❌ No script text found")
            return None

        json_string = script_text.group(1)
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON decode error: {e}")
            return None

    def _extract_is_illegally_occupied(self, soup: BeautifulSoup) -> bool:
        return soup.find("span", string="Ocupada ilegalmente") is not None

    def _extract_characteristics(self, data: dict) -> dict:
        characteristics = data.get("ad", {}).get("characteristics", {})
        return {
            "rooms": characteristics.get("roomNumber") or 0,
            "bathrooms": characteristics.get("bathNumber") or 0,
            "square_meters": characteristics.get("constructedArea") or 0,
            "has_garage": self._str_to_bool(characteristics.get("hasParking", "")),
            "has_garden": self._str_to_bool(characteristics.get("hasGarden", "")),
            "has_pool": self._str_to_bool(characteristics.get("hasSwimmingPool", "")),
            "has_terrace": self._str_to_bool(characteristics.get("hasTerrace", "")),
        }

    def _extract_condition(self, data: dict) -> dict:
        condition = data.get("ad", {}).get("condition", {})
        return {
            "is_new_development": self._str_to_bool(
                condition.get("isNewDevelopment", "")
            ),
            "needs_renovation": self._str_to_bool(
                condition.get("isNeedsRenovating", "")
            ),
            "is_in_good_condition": self._str_to_bool(
                condition.get("isGoodCondition", "")
            ),
        }

    def _extract_price(self, data: dict) -> float:
        return float(data.get("ad", {}).get("price", 0))

    def _extract_agency_name(self, data: dict) -> str:
        return data.get("agency", {}).get("name", "")

    def _extract_metadata(self, soup: BeautifulSoup, property_url: str) -> dict:
        return {
            "title": self._extract_title(soup),
            "description": self._extract_description(soup),
            "address": self._extract_address(soup),
            "location": self._extract_location(soup),
            "url": f"{BASE_URL}{property_url}",
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find("span", class_="main-info__title-main")
        return title_tag.get_text(strip=True) if title_tag else ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        desc_tag = soup.find("div", class_="ad-comment")
        return desc_tag.get_text(strip=True) if desc_tag else ""

    def _extract_address(self, soup: BeautifulSoup) -> str:
        address_tag = soup.find("span", class_="main-info__address-text")
        return address_tag.get_text(strip=True) if address_tag else ""

    def _extract_location(self, soup: BeautifulSoup) -> str:
        span = soup.find("span", class_="main-info__title-minor")
        return span.get_text(strip=True) if span else ""

    def _str_to_bool(self, value: str) -> bool:
        return value == "1"

    async def run(self):
        start_time = time.time()
        self.logger.info("🔍 Scraping Idealista asynchronously...")

        locations = self.database.get_locations()
        if not locations:
            self.logger.error("❌ No locations found in the database")
            return
        self.logger.info(f"✅ Found {len(locations)} locations in the database")

        async with AsyncSession(impersonate="chrome") as session:
            for location in locations:
                url = f"https://www.idealista.com{location.get('path').replace('mapa', '')}"
                self.logger.info(f"▶️ Starting to scrape: {url}")
                await self.scrape_page(url, session, location.get("id"))
                self.logger.info(f"✅ Finished scraping: {url}")

                if location != locations[-1]:
                    sleep_time = random.uniform(5, 15)
                    self.logger.info(
                        f"💤 Sleeping for {sleep_time:.2f} seconds before next location..."
                    )
                    await asyncio.sleep(sleep_time)

        self.logger.info(
            f"✅ Scraping finished in {time.time() - start_time:.2f} seconds"
        )

    async def scrape_page(self, url: str | None, session, location_id: str | None):
        if url is None or location_id is None:
            self.logger.error("❌ URL or location ID is None")
            return
        self.logger.info(f"Scraping page: {url}")
        r = await session.get(url)
        soup = BeautifulSoup(r.text, "lxml")

        property_links = await self._fetch_property_links(soup)

        properties = await asyncio.gather(
            *[self.get_property_data(session, link) for link in property_links]
        )

        valid_properties = [
            {
                **{k: v for k, v in p.model_dump().items() if k != "price"},
                "price_amount": p.price.get_amount(),
                "price_currency": p.price.get_currency(),
                "location_id": location_id,
            }
            for p in properties
            if p is not None
        ]

        if valid_properties:
            self.logger.info(
                f"Saving {len(valid_properties)} properties to database..."
            )
            self.database.insert_properties(valid_properties)
            self.logger.info(f"✅ {len(valid_properties)} properties saved to database")

        next_page_link = await self.get_next_page_link(soup)
        await self.scrape_page(next_page_link, session, location_id)

    async def _fetch_property_links(self, soup: BeautifulSoup):
        return [link.get("href") for link in soup.find_all("a", class_="item-link")]

    async def get_next_page_link(self, soup: BeautifulSoup) -> str | None:
        next_li = soup.find("li", class_="next")
        if next_li:
            next_path = next_li.find("a").get("href")
            return f"{BASE_URL}{next_path}"
        self.logger.debug("❌ No next page found")
        return None
