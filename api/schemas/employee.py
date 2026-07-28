from pydantic import BaseModel, ConfigDict
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    role: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None

class RestaurantEmployee(EmployeeBase):
    employee_id: int

    model_config = ConfigDict(from_attributes=True)