from Logger import Logger
from supabase import create_client, Client

import os
from dotenv import load_dotenv


class Database:
    def __init__(self, logger: Logger):
        load_dotenv()
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set up as env variables"
            )
        self.logger = logger
        self.client: Client = create_client(self.url, self.key)

    def insert_locations(self, locations: set[dict]) -> bool:
        self.logger.debug(f"locations received: {locations}")
        locations_list = list(locations)
        self.logger.debug(f"Inserting locations: {locations_list}")
        try:
            response = self.client.table("locations").insert(locations_list).execute()
            return len(response.data) > 0
        except Exception as e:
            self.logger.error(f"Error inserting locations: {e}")
            return False
