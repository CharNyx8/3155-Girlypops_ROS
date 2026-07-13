from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class MenuItemInventoryBase(BaseModel):
    item_id: int
    ingredient_id: int
    quantity_required: Decimal


class MenuItemInventoryCreate(MenuItemInventoryBase):
    pass


class MenuItemInventoryUpdate(BaseModel):
    quantity_required: Optional[Decimal] = None


class MenuItemInventoryOut(MenuItemInventoryBase):
    class Config:
        from_attributes = True