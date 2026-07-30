from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ReportBase(BaseModel):
    report_name: str
    generated_by_manager_id: Optional[int] = None


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    report_name: Optional[str] = None
    generated_by_manager_id: Optional[int] = None


class Report(ReportBase):
    report_id: int
    date_generated: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyRevenue(BaseModel):
    report_date: date
    order_count: int
    total_revenue: Decimal


class MenuPerformance(BaseModel):
    item_id: int
    item_name: str
    quantity_sold: int

    model_config = ConfigDict(from_attributes=True)