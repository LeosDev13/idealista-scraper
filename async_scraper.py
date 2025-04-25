import asyncio
import re
import time
import random
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession

from decimal import Decimal

from utils import parse_price
from Money import Money

BASE_URL = "https://www.idealista.com"
semaphore = asyncio.Semaphore(3)

# 🔄 Función asíncrona para obtener los detalles de una propiedad
async def fetch_property_details(session, property_url):
    async with semaphore:
        response = await  session.get(f"{BASE_URL}{property_url}")
        soup = BeautifulSoup(response.text, 'lxml')
        price_text = soup.find("span", class_="info-data-price")
        if price_text is None:
            print(f"❌ price text not found for property {property_url}")
            return
        price = parse_price(price_text.get_text())
        print(f"🏠 {property_url} → Precio: {price}")
        await asyncio.sleep(random.uniform(5, 15))  # Espera aleatoria


# 🔍 Función para extraer enlaces de propiedades de una página
async def fetch_property_links(session, soup):
    return [link.get('href') for link in soup.find_all("a", class_="item-link")]

async def get_next_page_link(session, soup):
    next_li = soup.find("li", class_="next")
    if next_li is None:
        print("❌ failed to find next li")
        return
    next_path = next_li.find("a").get("href")
    print("✅ next page")
    return f"{BASE_URL}{next_path}"


# 🏡 Función principal asíncrona
async def main():
    start_time = time.time()
    print("🔍 Scrapeando Idealista de forma asíncrona...")
    initial_url =  "https://www.idealista.com/geo/venta-viviendas/rodalies-premia-de-mar/con-precio-hasta_600000,metros-cuadrados-mas-de_120,chalets/"

    async with AsyncSession(impersonate="chrome") as session:
        await run_scraper(initial_url, session)
        
    print(f"✅ Tiempo total: {time.time() - start_time:.2f} segundos")


async def run_scraper(url: str | None, session):
    if url is None:
        return
    r = await session.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    
    property_links = await fetch_property_links(session, soup)

    await asyncio.gather(*[fetch_property_details(session, link) for link in property_links])

    next_page_link = await get_next_page_link(session, soup)

    await run_scraper(next_page_link, session)



# 🚀 Ejecutar el script asíncrono
if __name__ == "__main__":
    asyncio.run(main())
