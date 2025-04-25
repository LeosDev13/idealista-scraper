from decimal import Decimal
from Money import Money
import re
from constants import LOCATIONS_MAP, CURRENCY_MAP


def parse_price(price_str):
    match = re.match(r"([\d.,]+)\s*([€$£]?)", price_str)
    if not match:
        raise ValueError(f"Formato no válido: {price_str}")

    raw_amount, currency_symbol = match.groups()
    normalized_amount = raw_amount.replace(".", "").replace(",", ".")
    amount = Decimal(normalized_amount)

    currency = CURRENCY_MAP.get(currency_symbol, "UNKNOWN")

    return Money(amount=amount, currency=currency)


def get_location_from_id(location_id: str) -> str:
    return LOCATIONS_MAP.get(location_id)
