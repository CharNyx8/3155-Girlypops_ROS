from datetime import datetime
from typing import Optional

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