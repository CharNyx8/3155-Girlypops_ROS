from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InventoryBase(BaseModel):
    ingredient_name: str
    quantity: Decimal
    minimum_quantity: Decimal
    maintained_by_manager_id: Optional[int] = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    ingredient_name: Optional[str] = None
    quantity: Optional[Decimal] = None
    minimum_quantity: Optional[Decimal] = None
    maintained_by_manager_id: Optional[int] = None


class Inventory(InventoryBase):
    ingredient_id: int

    model_config = ConfigDict(from_attributes=True)