from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class PaymentBase(BaseModel):
    paymentMethod: str
    paymentStatus: str
    amount: Decimal


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    paymentMethod: Optional[str] = None
    paymentStatus: Optional[str] = None
    amount: Optional[Decimal] = None


class Payment(PaymentBase):
    paymentID: int

    class ConfigDict:
        from_attributes = True
