import asyncio
import time
import random
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
            print(f"🏠 {property_url} → Precio: {price}")
            await asyncio.sleep(random.uniform(5, 15))

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

        await self.run_scraper(next_page_link, session)


if __name__ == "__main__":
    scraper = IdealistaScraper()
    asyncio.run(scraper.run())
