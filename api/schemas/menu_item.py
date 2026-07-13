from typing import Optional
from pydantic import BaseModel
from decimal import Decimal


class MenuItemBase(BaseModel):
    item_name: str
    description: Optional[str] = None
    price: Decimal
    category: Optional[str] = None
    dietary_type: Optional[str] = None
    is_available: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    dietary_type: Optional[str] = None
    is_available: Optional[bool] = None


class MenuItem(MenuItemBase):
    item_id: int

    class ConfigDict:
        from_attributes = True