from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MenuItemBase(BaseModel):
    item_name: str
    description: Optional[str] = None
    price: Decimal
    category: Optional[str] = None
    dietary_type: Optional[str] = None
    is_available: bool = True
    created_by_manager_id: Optional[int] = None


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    dietary_type: Optional[str] = None
    is_available: Optional[bool] = None
    created_by_manager_id: Optional[int] = None


class MenuItem(MenuItemBase):
    item_id: int

    model_config = ConfigDict(from_attributes=True)