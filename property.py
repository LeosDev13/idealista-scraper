from pydantic import BaseModel
from Money import Money


class Property(BaseModel):
    price: Money
    title: str
    description: str
    address: str
    square_meters: int
    rooms: int
    has_garage: bool
    tags: list[str]
    price_per_square_meter: Money
    location: str
