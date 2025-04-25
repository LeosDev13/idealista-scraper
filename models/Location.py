from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Location:
    number_of_properties: int
    is_interest_zone: bool
    category: str
    path: str
    title: str
    id: str | None = field(default=None)
    created_at: datetime | None = field(default=None)
    updated_at: datetime | None = field(default=None)

    def as_dict(self) -> dict:
        return asdict(self)
