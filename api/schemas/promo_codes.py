from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class PromoCodeBase(BaseModel):
    discountAmount: Decimal
    expirationDate: datetime
    active: bool


class PromoCodeCreate(PromoCodeBase):
    promoCode: str


class PromoCodeUpdate(BaseModel):
    discountAmount: Optional[Decimal] = None
    expirationDate: Optional[datetime] = None
    active: Optional[bool] = None


class PromoCode(PromoCodeBase):
    promoCode: str

    class ConfigDict:
        from_attributes = True
