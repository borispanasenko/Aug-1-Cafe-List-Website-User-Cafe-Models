from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import List, Optional
from uuid import UUID
from .review_schemas import ReviewResponse
from datetime import datetime  # noqa: F401


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str
    full_name: Optional[str] = None
    location: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isdigit() for c in v) or not any(c.isupper() for c in v):
            raise ValueError('Password must contain digit and uppercase letter')
        return v


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    location: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    username: Optional[str] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v and (not any(c.isdigit() for c in v) or not any(c.isupper() for c in v)):
            raise ValueError('Password must contain digit and uppercase letter')
        return v


class UserInDB(UserRead):
    hashed_password: str


class UserWithReviewsResponse(UserRead):
    reviews: List[ReviewResponse] = []

    class Config:
        from_attributes = True
