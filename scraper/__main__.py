import asyncio

from core.Database import Database

# from LocationsScraper import LocationsScraper
from core.Logger import Logger
from scraper.IdealistaScraper import IdealistaScraper


async def main():
    logger = Logger(level="DEBUG")
    database = Database(logger)

    #  locations_scraper = LocationsScraper(logger, database)
    # await locations_scraper.run()
    idealista_scraper = IdealistaScraper(database, logger)
    await idealista_scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
