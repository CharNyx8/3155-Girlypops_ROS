from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderDetailsCreate(BaseModel):
    order_id: int
    item_id: int
    quantity: int = Field(default=1, ge=1)
    special_instructions: Optional[str] = None


class OrderDetailsUpdate(BaseModel):
    quantity: Optional[int] = None
    special_instructions: Optional[str] = None


class OrderDetails(BaseModel):
    order_detail_id: int
    order_id: int
    item_id: int
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal
    special_instructions: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)