from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class RestaurantManagerBase(BaseModel):
    name: str
    email: EmailStr


class RestaurantManagerCreate(RestaurantManagerBase):
    pass


class RestaurantManagerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class RestaurantManager(RestaurantManagerBase):
    manager_id: int

    model_config = ConfigDict(from_attributes=True)