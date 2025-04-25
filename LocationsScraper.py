import asyncio
import time
from Database import Database
from Location import Location
from curl_cffi.requests import AsyncSession
from Logger import Logger
import itertools
from constants import LOCATIONS_BASE_URL


class LocationsScraper:
    MAX_CONCURRENT_REQUESTS = 10

    def __init__(self, logger: Logger, database: Database):
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)
        self.logger = logger
        self.database = database
        self.locations = set()

    async def run(self):
        start_time = time.time()
        self.logger.info("🔍 Scraping Locations...")
        combinations = [
            "".join(c)
            for c in itertools.product("abcdefghijklmnopqrstuvwxyz", repeat=2)
        ]

        async with self.semaphore:
            async with AsyncSession(impersonate="chrome") as session:
                tasks = [
                    self._fetch_locations(session, f"{LOCATIONS_BASE_URL}{combination}")
                    for combination in combinations
                ]
                await asyncio.gather(*tasks)

        response = self.database.insert_locations(self.locations)
        self.logger.debug(f"locations insert response: {response}")

        self.logger.info(f"✅ Tiempo total: {time.time() - start_time:.2f} segundos")

    async def _fetch_locations(self, session, url):
        headers = {
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "cookie": 'userUUID=ab24d6f7-ad9d-4621-9483-73201b9368ec; didomi_token=eyJ1c2VyX2lkIjoiMTkwMDg5Y2ItYzkyZi02MjMyLTk5NWItNDYyMTMwNjAwZDZkIiwiY3JlYXRlZCI6IjIwMjQtMDYtMTFUMTg6NDM6MjguMDE4WiIsInVwZGF0ZWQiOiIyMDI0LTA2LTExVDE4OjQzOjI5LjYzM1oiLCJ2ZW5kb3JzIjp7ImRpc2FibGVkIjpbImdvb2dsZSIsImM6bGlua2VkaW4tbWFya2V0aW5nLXNvbHV0aW9ucyIsImM6bWl4cGFuZWwiLCJjOmFidGFzdHktTExrRUNDajgiLCJjOmhvdGphciIsImM6YmVhbWVyLUg3dHI3SGl4IiwiYzp0ZWFsaXVtY28tRFZEQ2Q4WlAiLCJjOnRpa3Rvay1LWkFVUUxaOSIsImM6Z29vZ2xlYW5hLTRUWG5KaWdSIiwiYzppZGVhbGlzdGEtTHp0QmVxRTMiLCJjOmlkZWFsaXN0YS1mZVJFamUyYyIsImM6Y29udGVudHNxdWFyZSIsImM6bWljcm9zb2Z0Il19LCJwdXJwb3NlcyI6eyJkaXNhYmxlZCI6WyJnZW9sb2NhdGlvbl9kYXRhIiwiZGV2aWNlX2NoYXJhY3RlcmlzdGljcyJdfSwidmVyc2lvbiI6MiwiYWMiOiJBQUFBLkFBQUEifQ==; euconsent-v2=CQAC8MAQAC8MAAHABBENA4EgAAAAAAAAAAAAAAAAAACkoAMAAQUiKQAYAAgpEQgAwABBSIdABgACCkQSADAAEFIg.YAAAAAAAAAAA; smc="{}"; utag_main__prevCompleteClickName=; askToSaveAlertPopUp=true; cookieSearch-1="/geo/venta-viviendas/rodalies-premia-de-mar/:1740248030254"; _last_search=officialZone; contact30f25d28-2c5a-4303-83dc-57f4686ea266="{\'maxNumberContactsAllow\':10}"; send30f25d28-2c5a-4303-83dc-57f4686ea266="{}"; SESSION=b736c720ecc0095b~30f25d28-2c5a-4303-83dc-57f4686ea266; utag_main__sn=17; utag_main__prevTsUrl=https%3A%2F%2Fwww.idealista.com%2Finmueble%2F104686009%2F%3Bexp-1741456567071; utag_main__prevTsReferrer=%3Bexp-1741456567071; utag_main__prevTsSource=Direct traffic%3Bexp-1741456567071; utag_main__prevTsCampaign=organicTrafficByTm%3Bexp-1741456567071; utag_main__prevTsProvider=%3Bexp-1741456567071; utag_main__prevEventLink=; utag_main__prevEventView=254-idealista/404 >  > 400 >  >  > www.idealista.com/es/locationsSuggest%3Bexp-1741456783852; utag_main__prevLevel2=254-idealista/404%3Bexp-1741456783852; datadome=G4Sk4qVAljM1OTr1udFSFQhovFKg8H~1AC06hXsp3~mP9AnFetdkKjwaDzIu_43yrpylFoW0gClWtG86UzA0sQoVu1nYm97hAmCF146UPED27AlwK85qBpCgw5~hY8uw',
        }

        response = await session.get(url, headers=headers)
        self.logger.debug(f"Requested URL: {response.request.url}")
        self.logger.debug(response.text)
        locations_json = response.json()

        for location_json in locations_json:
            location = Location(
                number_of_properties=location_json["count"],
                title=location_json["text"],
                is_interest_zone=location_json["zoneOfInterest"],
                category=location_json["category"],
                path=location_json["url"],
            )
            self.locations.add(frozenset(location.as_dict().items()))

        time.sleep(0.5)
