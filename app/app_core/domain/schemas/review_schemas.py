from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreateSchema(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponseSchema(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    user_name: str

    class Config:
        from_attributes = True
