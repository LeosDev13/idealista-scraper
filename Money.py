from pydantic import BaseModel, field_validator
from decimal import Decimal

class Money(BaseModel):
    amount: Decimal
    currency: str

    @field_validator('currency')
    def validate_currency(cls, v):
        valid_currencies = {"EUR", "USD", "GBP"}
        if v not in valid_currencies:
            raise ValueError(f"Moneda no válida: {v}")
        return v

    @field_validator('amount')
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError(f"El monto no puede ser negativo")
        return v

    def __str__(self):
        symbols = {'EUR': '€', 'USD': '$', 'GBP': '£'}
        return f"{self.amount:.2f} {symbols.get(self.currency, '')}"


