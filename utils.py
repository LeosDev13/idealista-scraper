from decimal import Decimal
from Money import Money
import re


def parse_price(price_str):
    match = re.match(r'([\d.,]+)\s*([€$£]?)', price_str)
    if not match:
        raise ValueError(f"Formato no válido: {price_str}")

    raw_amount, currency_symbol = match.groups()
    normalized_amount = raw_amount.replace('.', '').replace(',', '.')
    amount = Decimal(normalized_amount)

    currency_map = {'€': 'EUR', '$': 'USD', '£': 'GBP'}
    currency = currency_map.get(currency_symbol, 'UNKNOWN')

    return Money(amount=amount, currency=currency)
