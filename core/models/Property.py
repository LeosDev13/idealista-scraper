from pydantic import BaseModel

from core.models.Money import Money


class Property(BaseModel):
    id: str
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
    agency_name: str
    location: str
    is_illegally_occupied: bool
    url: str

    @property
    def price_per_square_meter(self) -> float:
        if self.square_meters == 0:
            return 0.0  # evita división por cero
        return float(self.price.amount) / self.square_meters

    def to_dict(self) -> dict:
        return self.model_dump()
