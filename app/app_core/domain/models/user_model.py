from __future__ import annotations

from sqlalchemy import String
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
