from pydantic import BaseModel, EmailStr
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    hasAccount: bool = False

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    customerID: int

    class Config:
        from_attributes = True 