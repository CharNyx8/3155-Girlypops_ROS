from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MenuItemInventoryBase(BaseModel):
    item_id: int
    ingredient_id: int
    quantity_required: Decimal


class MenuItemInventoryCreate(MenuItemInventoryBase):
    pass


class MenuItemInventoryUpdate(BaseModel):
    quantity_required: Optional[Decimal] = None


class MenuItemInventory(MenuItemInventoryBase):
    model_config = ConfigDict(from_attributes=True)