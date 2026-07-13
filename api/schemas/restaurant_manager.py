from typing import Optional
from pydantic import BaseModel


class RestaurantManagerBase(BaseModel):
    name: str
    email: str


class RestaurantManagerCreate(RestaurantManagerBase):
    pass

class RestaurantManagerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class RestaurantManager(RestaurantManagerBase):
    manager_id: int

    class ConfigDict:
        from_attributes = True