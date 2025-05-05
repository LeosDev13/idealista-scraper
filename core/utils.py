import re

from models.Money import Money

from constants import LOCATIONS_MAP


def get_location_from_id(location_id: str) -> str:
    return LOCATIONS_MAP.get(location_id)
