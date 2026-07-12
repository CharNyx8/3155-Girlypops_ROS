from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    role: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    employee_id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None

class RestaurantEmployeeSchema(EmployeeBase):
    id: int

    class ConfigDict:
        from_attributes = True