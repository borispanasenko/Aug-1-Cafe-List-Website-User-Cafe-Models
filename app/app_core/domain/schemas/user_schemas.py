from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import List, Optional
from uuid import UUID
from .review_schemas import ReviewResponseSchema
from datetime import datetime  # noqa: F401


class UserCreateSchema(BaseModel):
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


class UserReadSchema(BaseModel):
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


class UserUpdateSchema(BaseModel):
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


class UserInDBSchema(UserReadSchema):
    hashed_password: str


class UserWithReviewsResponseSchema(UserReadSchema):
    reviews: List[ReviewResponseSchema] = []

    class Config:
        from_attributes = True
