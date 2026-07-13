from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ReportBase(BaseModel):
    report_name: str
    date_generated: datetime


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    report_name: Optional[str] = None
    date_generated: Optional[datetime] = None


class Report(ReportBase):
    report_id: int
    generated_by_manager_id: Optional[int] = None

    class ConfigDict:
        from_attributes = True