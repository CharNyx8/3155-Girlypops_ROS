from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    order_id: int
    payment_method: str
    payment_status: str
    amount: Decimal


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    order_id: Optional[int] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    amount: Optional[Decimal] = None


class Payment(PaymentBase):
    payment_id: int

    model_config = ConfigDict(from_attributes=True)