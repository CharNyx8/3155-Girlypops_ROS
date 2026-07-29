from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderDetailsBase(BaseModel):
    order_id: int
    item_id: int
    quantity: int = 1
    unit_price: Decimal
    special_instructions: Optional[str] = None


class OrderDetailsCreate(OrderDetailsBase):
    pass


class OrderDetailsUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    special_instructions: Optional[str] = None


class OrderDetails(OrderDetailsBase):
    order_detail_id: int

    model_config = ConfigDict(from_attributes=True)