from core.Database import Database
from core.Logger import Logger


class LocationService:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.db = Database(logger)

    def get_all_locations(self) -> list[dict]:
        try:
            locations = self.db.get_locations()
            self.logger.info(f"Retrieved {len(locations)} locations from database")
            return locations
        except Exception as e:
            self.logger.error(f"Error retrieving locations: {str(e)}")
            return []
