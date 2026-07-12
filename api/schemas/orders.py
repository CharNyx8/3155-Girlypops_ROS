from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from .order_details import OrderDetail


class OrderBase(BaseModel):
    orderStatus: str
    orderType: str
    totalPrice: Decimal
    estimatedTime: int


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    orderDate: Optional[datetime] = None
    orderStatus: Optional[str] = None
    orderType: Optional[str] = None
    totalPrice: Optional[Decimal] = None
    estimatedTime: Optional[int] = None


class Order(OrderBase):
    orderID: int
    orderDate: Optional[datetime] = None
    order_details: list[OrderDetail] = None

    class ConfigDict:
        from_attributes = True
