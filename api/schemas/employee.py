from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    employeeID: str
    name: str
    role: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    employeeID: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None

class RestaurantEmployeeSchema(EmployeeBase):
    id: int

    class Config:
        from_attributes = True