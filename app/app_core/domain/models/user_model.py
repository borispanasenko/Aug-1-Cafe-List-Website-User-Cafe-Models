from __future__ import annotations
from typing import Optional
from uuid import UUID
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database import Base


class UserModel(SQLAlchemyBaseUserTableUUID, Base):
    """
    fastapi-users SQLAlchemyBaseUserTableUUID predefined fields:

    - id: UUID (generates automatically)
    - email: Required for authentication
    - hashed_password: Hashed password
    - is_active: Active user flag
    - is_superuser: Superuser flag
    - is_verified: Verification flag


    """
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
