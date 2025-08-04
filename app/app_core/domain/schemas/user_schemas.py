from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserReadSchema(BaseModel):
    id: UUID
    email: EmailStr
    username: str


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    username: str


class UserUpdateSchema(BaseModel):
    ...
