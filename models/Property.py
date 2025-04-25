from pydantic import BaseModel
from models.Money import Money


class Property(BaseModel):
    price: Money
    title: str
    description: str
    address: str
    square_meters: int
    rooms: int
    bathrooms: int
    has_garage: bool
    has_garden: bool
    has_pool: bool
    has_terrace: bool
    is_new_development: bool
    needs_renovation: bool
    is_in_good_condition: bool
    has_terrace: bool
    agency_name: str
    location: str

    @property
    def price_per_square_meter(self) -> float:
        self.price_per_square_meter = self.price / self.square_meters
