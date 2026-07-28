from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PromoCodeBase(BaseModel):
    promo_code: str
    discount_amount: Decimal
    expiration_date: datetime
    is_active: bool = True
    manager_id: int


class PromoCodeCreate(PromoCodeBase):
    pass


class PromoCodeUpdate(BaseModel):
    discount_amount: Optional[Decimal] = None
    expiration_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    manager_id: Optional[int] = None


class PromoCode(PromoCodeBase):
    model_config = ConfigDict(from_attributes=True)