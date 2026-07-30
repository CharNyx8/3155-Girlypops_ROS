from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: Literal["Card", "Cash", "Gift Card"]


class PaymentUpdate(BaseModel):
    payment_method: Optional[Literal["Card", "Cash", "Gift Card"]] = None
    payment_status: Optional[Literal["Pending", "Paid", "Failed", "Refunded"]] = None


class Payment(BaseModel):
    payment_id: int
    order_id: int
    payment_method: str
    payment_status: str
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)