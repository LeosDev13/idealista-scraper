import os

from dotenv import load_dotenv
from supabase import Client, create_client

from core.Logger import Logger


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

    def insert_locations(self, locations: list[dict]) -> bool:
        response = self.client.table("Locations").select("*").execute()
        self.logger.debug(f"supabase connection was succeded: {response}")
        try:
            response = self.client.table("Locations").insert(locations).execute()
            if response.data is None:
                self.logger.error(f"Supabase insert failed: {response}")
                return False
            return len(response.data) > 0
        except Exception as e:
            self.logger.error(f"Error inserting locations: {str(e)}")
            return False

    def insert_properties(self, properties: list[dict]) -> bool:
        """
        Inserta una lista de propiedades en la base de datos.
        Si una propiedad falla, continúa con las siguientes.

        Args:
            properties: Lista de diccionarios con los datos de las propiedades

        Returns:
            bool: True si al menos una propiedad se insertó correctamente
        """
        success_count = 0
        failure_count = 0

        for property in properties:
            try:
                response = self.client.table("Properties").insert(property).execute()
                if response.data is not None:
                    success_count += 1
                else:
                    failure_count += 1
                    self.logger.error(
                        f"Database insert failed for property {property.get('id', 'unknown')}: {response}"
                    )
            except Exception as e:
                failure_count += 1
                self.logger.error(
                    f"Error inserting property {property.get('id', 'unknown')}: {str(e)}"
                )

        self.logger.info(
            f"Properties insertion complete. Success: {success_count}, Failures: {failure_count}"
        )
        return success_count > 0

    def get_locations(self) -> list[dict]:
        try:
            response = (
                self.client.table("Locations")
                .select("*")
                .order("number_of_properties", desc=True)
                .execute()
            )
            if response.data is None:
                self.logger.error(f"Supabase get failed: {response}")
                return []
            return response.data
        except Exception as e:
            self.logger.error(f"Error getting locations: {str(e)}")
            return []
