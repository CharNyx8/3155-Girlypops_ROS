from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderBase(BaseModel):
    order_status: str
    order_type: str
    total_price: Decimal
    estimated_time: int
    promo_code: Optional[str] = None
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    order_status: Optional[str] = None
    order_type: Optional[str] = None
    total_price: Optional[Decimal] = None
    estimated_time: Optional[int] = None
    promo_code: Optional[str] = None
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None


class OrderTracking(BaseModel):
    order_id: int
    order_status: str
    order_type: str
    estimated_time: int

class Order(OrderBase):
    order_id: int
    order_date: datetime

    model_config = ConfigDict(from_attributes=True)