from typing import Optional
from pydantic import BaseModel
from decimal import Decimal


class InventoryBase(BaseModel):
    ingredient_name: str
    quantity: Decimal
    minimum_quantity: Decimal


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    ingredient_name: Optional[str] = None
    quantity: Optional[Decimal] = None
    minimum_quantity: Optional[Decimal] = None


class Inventory(InventoryBase):
    ingredient_id: int
    maintained_by_manager_id: Optional[int] = None

    class Config:
        from_attributes = True
