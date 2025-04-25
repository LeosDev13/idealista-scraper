import asyncio
from datetime import datetime
import uuid
import random
import time
from typing import Any
from Database import Database
from Location import Location
from curl_cffi.requests import AsyncSession
from Logger import Logger
import itertools
from constants import LOCATIONS_BASE_URL


class LocationsScraper:
    MAX_CONCURRENT_REQUESTS = 3

    def __init__(self, logger: Logger, database: Database):
        self.headers = {
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "cookie": 'userUUID=ab24d6f7-ad9d-4621-9483-73201b9368ec; didomi_token=eyJ1c2VyX2lkIjoiMTkwMDg5Y2ItYzkyZi02MjMyLTk5NWItNDYyMTMwNjAwZDZkIiwiY3JlYXRlZCI6IjIwMjQtMDYtMTFUMTg6NDM6MjguMDE4WiIsInVwZGF0ZWQiOiIyMDI0LTA2LTExVDE4OjQzOjI5LjYzM1oiLCJ2ZW5kb3JzIjp7ImRpc2FibGVkIjpbImdvb2dsZSIsImM6bGlua2VkaW4tbWFya2V0aW5nLXNvbHV0aW9ucyIsImM6bWl4cGFuZWwiLCJjOmFidGFzdHktTExrRUNDajgiLCJjOmhvdGphciIsImM6YmVhbWVyLUg3dHI3SGl4IiwiYzp0ZWFsaXVtY28tRFZEQ2Q4WlAiLCJjOnRpa3Rvay1LWkFVUUxaOSIsImM6Z29vZ2xlYW5hLTRUWG5KaWdSIiwiYzppZGVhbGlzdGEtTHp0QmVxRTMiLCJjOmlkZWFsaXN0YS1mZVJFamUyYyIsImM6Y29udGVudHNxdWFyZSIsImM6bWljcm9zb2Z0Il19LCJwdXJwb3NlcyI6eyJkaXNhYmxlZCI6WyJnZW9sb2NhdGlvbl9kYXRhIiwiZGV2aWNlX2NoYXJhY3RlcmlzdGljcyJdfSwidmVyc2lvbiI6MiwiYWMiOiJBQUFBLkFBQUEifQ==; euconsent-v2=CQAC8MAQAC8MAAHABBENA4EgAAAAAAAAAAAAAAAAAACkoAMAAQUiKQAYAAgpEQgAwABBSIdABgACCkQSADAAEFIg.YAAAAAAAAAAA; smc="{}"; utag_main__prevCompleteClickName=; _last_search=interestZone; utag_main__prevEventLink=; contact7d4f20ec-3cbf-458a-af95-ddd8e5c05892="{\'maxNumberContactsAllow\':10}"; cookieSearch-1="/geo/venta-viviendas/primera-linea-de-playa-playa-blanca-lanzarote/:1743269085890"; send7d4f20ec-3cbf-458a-af95-ddd8e5c05892="{}"; SESSION=b736c720ecc0095b~c6b8b328-302a-4bea-9e27-abd465406cb4; utag_main__sn=26; utag_main_ses_id=1743365029554%3Bexp-session; utag_main__prevTsUrl=https%3A%2F%2Fwww.idealista.com%2F%3Bexp-1743368629566; utag_main__prevTsReferrer=https://www.idealista.com/%3Bexp-1743368629566; utag_main__prevTsSource=Portal sites%3Bexp-1743368629566; utag_main__prevTsCampaign=organicTrafficByTm%3Bexp-1743368629566; utag_main__prevTsProvider=%3Bexp-1743368629566; utag_main__ss=0%3Bexp-session; utag_main__pn=2%3Bexp-session; utag_main__se=4%3Bexp-session; utag_main__st=1743366841375%3Bexp-session; utag_main__prevEventView=010-idealista/home > portal > > > > viewHome%3Bexp-1743368641386; utag_main__prevLevel2=010-idealista/home%3Bexp-1743368641386; datadome=ztgHE2NL3wpTmIznQV_K_Ghn4O9BJ71H_IbWWPJ3WpnZxzST7IwVl87R5aSR4ZukX7Zytpa_bik9i5B1dq7us0BCd669e0LvMysGBKYEjfpV19ILmz2FQJBN5bz9vN3D',
        }
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)
        self.logger = logger
        self.database = database
        self.locations: list[dict[str, Any]] = []

    async def run(self):
        start_time = time.time()
        self.logger.info("🔍 Scraping Locations...")

        combinations = self._generate_combinations()

        async with AsyncSession(impersonate="chrome") as session:
            tasks = []
            # Usar semáforo para controlar concurrencia
            for combination in combinations:
                task = self._fetch_locations(
                    session, f"{LOCATIONS_BASE_URL}{combination}"
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

        response = self.database.insert_locations(self.locations)
        self.logger.debug(f"Insert locations result: {response}")

        elapsed_time = time.time() - start_time
        self.logger.info(f"✅ Total time: {elapsed_time:.2f} segundos")
        self.logger.info(f"📊 Found locations: {len(self.locations)}")

    async def _fetch_locations(self, session, url):
        async with self.semaphore:
            response = await session.get(url, headers=self.headers)
            self.logger.debug(f"Requested URL: {response.request.url}")

            locations_json = response.json()

            for location_json in locations_json:
                title = (
                    location_json.get("text").replace("<b>", "").replace("</b>", "")
                    if location_json.get("text")
                    else ""
                )
                location = Location(
                    number_of_properties=location_json["count"],
                    title=title,
                    is_interest_zone=location_json["zoneOfInterest"],
                    category=location_json["category"],
                    path=location_json["url"],
                    id=str(uuid.uuid4()),
                    created_at=datetime.utcnow().isoformat(),
                    updated_at=datetime.utcnow().isoformat(),
                )
                self.locations.append(location.as_dict())
            await asyncio.sleep(random.uniform(5, 15))

    def _save_locations(self):
        saved_count = 0
        error_count = 0

        for location in self.locations:
            try:
                response = self.database.insert_location(location)
                saved_count += 1
                self.logger.debug(f"Location insert response: {response}")
            except Exception as e:
                error_count += 1
                self.logger.error(f"Error saving a location: {str(e)}")

        self.logger.info(f"📝 Saved: {saved_count}, Failed: {error_count}")

    def _generate_combinations(self):
        return [
            "".join(c)
            for c in itertools.product("abcdefghijklmnopqrstuvwxyz", repeat=2)
        ]
