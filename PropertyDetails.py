from dataclasses import dataclass


@dataclass
class PropertyDetails:
    room_number: int | None
    bath_number: int | None
    price: str | None
    has_parking: bool | None
    has_garden: bool | None
    has_swimming_pool: bool | None
    has_terrace: bool | None
    m2: str | None
    is_new_development: bool | None
    needs_renovation: bool | None
    is_in_good_condition: bool | None
    agency_name: str | None
