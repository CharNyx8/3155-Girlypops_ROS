from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class PaymentBase(BaseModel):
    paymentMethod: str
    paymentStatus: str
    amount: Decimal


class PaymentCreate(PaymentBase):
    orderID: int


class PaymentUpdate(BaseModel):
    orderID: Optional[int] = None
    paymentMethod: Optional[str] = None
    paymentStatus: Optional[str] = None
    amount: Optional[Decimal] = None


class Payment(PaymentBase):
    paymentID: int
    orderID: int

    class Config:
        from_attributes = True