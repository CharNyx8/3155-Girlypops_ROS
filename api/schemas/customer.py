from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    has_account: bool = False

class CustomerCreate(CustomerBase):
    pass
class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    has_account: Optional[bool] = None


class CustomerResponse(CustomerBase):
    customerID: int

    model_config = ConfigDict(from_attributes=True)