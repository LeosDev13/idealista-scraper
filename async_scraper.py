import asyncio
import re
import json
import time
import random
from collections import namedtuple
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from db import Db
from utils import parse_price

BASE_URL = "https://www.idealista.com"


class IdealistaScraper:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(3)
        self.db = Db()
        self.session = None

    async def fetch_property_details(self, session, property_url):
        async with self.semaphore:
            response = await session.get(f"{BASE_URL}{property_url}")
            soup = BeautifulSoup(response.text, 'lxml')
            price_text = soup.find("span", class_="info-data-price")
            if price_text is None:
                print(f"❌ price text not found for property {property_url}")
                return
            price = parse_price(price_text.get_text())
            title = await self.get_property_title(session, soup)
            features =  self.get_features(soup)
            # price=price.get_amount()
            print(f"🏠 {property_url} → Price: {price} -> Title: {title}")
            print(f"Room number -> {features.room_number} -> Bath number: {features.bath_number}")

            await asyncio.sleep(random.uniform(5,15))

    def get_features(self, soup):
        Features = namedtuple("Features", ["room_number", "bath_number"])
        script_tag = soup.find(
            "script", string=re.compile(r"window\.utag_data\s*=\s*utag_data")
        )
        if script_tag is None:
            print("❌ script tag not found")
            return
        print("✅script tag found")
        json_data = self.extract_utag_data(script_tag)

        characteristics = json_data.get("ad", {}).get("characteristics", {})
        room_number = characteristics.get("roomNumber")
        bath_number = characteristics.get("bathNumber")

        features = Features(room_number, bath_number)
        return features

    def extract_utag_data(self, script):
        regex = re.compile(r"var\s+utag_data\s*=\s*(\{.*?\});", re.DOTALL)
        script_text = regex.search(script.text)

        if script_text is None:
            return None

        json_string = script_text.group(1)

        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"❌ json decode error: {e}")

        return None

    async def get_property_title(self, session, soup):
        title_span = soup.find("span", class_="main-info__title-main")
        if title_span is None:
            print("Property title not found")
            return
        return title_span.get_text()

    async def fetch_property_links(self, session, soup):
        return [link.get('href') for link in soup.find_all("a", class_="item-link")]

    async def get_next_page_link(self, session, soup):
        next_li = soup.find("li", class_="next")
        if next_li is None:
            print("❌ failed to find next li")
            return
        next_path = next_li.find("a").get("href")
        return f"{BASE_URL}{next_path}"

    async def run(self):
        start_time = time.time()
        print("🔍 Scraping Idealista asynchronous...")
        initial_url = "https://www.idealista.com/geo/venta-viviendas/rodalies-premia-de-mar/con-precio-hasta_600000,metros-cuadrados-mas-de_120,chalets/"

        async with AsyncSession(impersonate="chrome") as session:
            await self.scrape_page(initial_url, session)

        print(f"✅ Tiempo total: {time.time() - start_time:.2f} segundos")

    async def scrape_page(self, url: str | None, session):
        if url is None:
            return
        r = await session.get(url)
        soup = BeautifulSoup(r.text, "lxml")

        property_links = await self.fetch_property_links(session, soup)

        await asyncio.gather(*[self.fetch_property_details(session, link) for link in property_links])

        next_page_link = await self.get_next_page_link(session, soup)

        await self.scrape_page(next_page_link, session)


if __name__ == "__main__":
    scraper = IdealistaScraper()
    asyncio.run(scraper.run())
