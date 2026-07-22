from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    customerID: int
    item_id: int

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(
        default = None,
        ge = 1,
        le = 5
    )
    comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    reviewID: int
    reviewDate: date

    class Config:
        from_attributes = True