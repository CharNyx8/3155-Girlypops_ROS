from typing import Optional
from pydantic import BaseModel, EmailStr


class RestaurantManagerBase(BaseModel):
    name: str
    email: EmailStr


class RestaurantManagerCreate(RestaurantManagerBase):
    pass

class RestaurantManagerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class RestaurantManager(RestaurantManagerBase):
    manager_id: int

    class Config:
        from_attributes = True