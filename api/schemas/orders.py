from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    order_status: str
    order_type: str
    estimated_time: int
    promo_code: Optional[str] = None
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None


class OrderUpdate(BaseModel):
    order_status: Optional[str] = None
    order_type: Optional[str] = None
    estimated_time: Optional[int] = None
    promo_code: Optional[str] = None
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None


class OrderTracking(BaseModel):
    order_id: int
    order_status: str
    order_type: str
    estimated_time: int

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    order_id: int
    order_date: datetime
    order_status: str
    order_type: str
    total_price: Decimal
    estimated_time: int
    promo_code: Optional[str] = None
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)