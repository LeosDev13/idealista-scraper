import asyncio
import time
import re
import json
import random

from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

from models.PropertyDetails import PropertyDetails
from models.Property import Property
from core.Logger import Logger
from constants.constants import BASE_URL


class IdealistaScraper:
    def __init__(self, logger: Logger):
        self.semaphore = asyncio.Semaphore(3)
        self.session = None
        self.logger = logger

    async def get_property_data(self, session, property_url: str) -> Property | None:
        details = self._fetch_property_details(session, property_url)
        if details:
            return Property(**details)

        self.logger.debug(f"❌ no details found in property: {property_url}")
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
    ) -> PropertyDetails | None:
        json_data = self._extract_utag_data(soup)
        if not json_data:
            return None

        return self.PropertyDetails(
            **self._extract_characteristics(json_data),
            **self._extract_condition(json_data),
            price=self._extract_price(json_data),
            agency_name=self._extract_agency_name(json_data),
            **self._extract_metadata(soup, property_url),
            is_illegally_ocuppied=self._extract_is_illegally_ocuppied(soup),
        )

    def _extract_is_illegaly_ocuppied(self, soup) -> bool:
        is_illegally_ocuppied_tag = soup.find("span", string="Ocupada ilegalmente")

        if is_illegally_ocuppied_tag:
            return True
        return False

    def _extract_characteristics(self, data: dict) -> dict:
        characteristics = data.get("ad", {}).get("characteristics", {})
        return {
            "room_number": characteristics.get("roomNumber"),
            "bath_number": characteristics.get("bathNumber"),
            "m2": characteristics.get("constructedArea"),
            "has_parking": self._str_to_bool(characteristics.get("hasParking", "")),
            "has_garden": self._str_to_bool(characteristics.get("hasGarden", "")),
            "has_swimming_pool": self._str_to_bool(
                characteristics.get("hasSwimmingPool", "")
            ),
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

    def _extract_price(self, data: dict) -> str | None:
        return data.get("ad", {}).get("price")

    def _extract_agency_name(self, data: dict) -> str | None:
        return data.get("agency", {}).get("name")

    def _extract_metadata(self, soup: BeautifulSoup, property_url: str) -> dict:
        return {"title": self._extract_title(soup), "url": property_url}

    def _extract_utag_data(self, script):
        regex = re.compile(r"var\s+utag_data\s*=\s*(\{.*?\});", re.DOTALL)
        script_text = regex.search(script.text)

        if script_text is None:
            return None

        json_string = script_text.group(1)

        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ json decode error: {e}")

        return None

    async def get_property_title(self, session, soup):
        title_span = soup.find("span", class_="main-info__title-main")
        if title_span is None:
            self.logger.error("Property title not found")
            return
        return title_span.get_text()

    async def _fetch_property_links(self, session, soup):
        return [link.get("href") for link in soup.find_all("a", class_="item-link")]

    async def get_next_page_link(self, session, soup):
        next_li = soup.find("li", class_="next")
        if next_li is None:
            self.logger.error("❌ failed to find next li")
            return
        next_path = next_li.find("a").get("href")
        return f"{BASE_URL}{next_path}"

    async def run(self):
        start_time = time.time()
        self.logger.info("🔍 Scraping Idealista asynchronous...")
        initial_url = "https://www.idealista.com/geo/venta-viviendas/rodalies-premia-de-mar/con-precio-hasta_600000,metros-cuadrados-mas-de_120,chalets/"

        async with AsyncSession(impersonate="chrome") as session:
            await self.scrape_page(initial_url, session)

        self.logger.info(f"✅ Tiempo total: {time.time() - start_time:.2f} segundos")

    async def scrape_page(self, url: str | None, session):
        if url is None:
            return
        r = await session.get(url)
        soup = BeautifulSoup(r.text, "lxml")

        property_links = await self._fetch_property_links(session, soup)

        await asyncio.gather(
            *[self._fetch_property_details(session, link) for link in property_links]
        )

        next_page_link = await self.get_next_page_link(session, soup)

        await self.scrape_page(next_page_link, session)

    def convert_string_to_bool(self, value: str) -> bool:
        return value == "1"
