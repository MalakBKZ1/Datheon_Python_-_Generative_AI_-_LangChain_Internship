from typing import List, Optional

from pydantic import BaseModel, field_validator


class Item(BaseModel):
    description: str
    quantity: int
    unit_price: float

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("La quantité doit être supérieure à 0")
        return v

    @field_validator("unit_price")
    @classmethod
    def price_not_negative(cls, v):
        if v < 0:
            raise ValueError("Le prix unitaire ne peut pas être négatif")
        return v


class Invoice(BaseModel):
    invoice_number: str
    date: str
    client_name: str
    items: List[Item]
    total: float
    currency: Optional[str] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None