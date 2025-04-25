from Logger import Logger
# from LocationsScraper import LocationsScraper
from IdealistaScraper import IdealistaScraper

BASE_URL = "https://www.idealista.com"

async def main():
    logger = Logger(level="DEBUG")

    idealista_scraper = IdealistaScraper(logger)
    await idealista_scraper.run()

if __name__ == "__main__":
    # run only one time and save it to idealista, we do not need to run multiple times because the locations does not change
    # locations_scraper = LocationsScraper()
    asyncio.run(main())
