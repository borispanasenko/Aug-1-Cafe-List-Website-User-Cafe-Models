from __future__ import annotations
from app.infrastructure.database import Base
from typing import List, TYPE_CHECKING
from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from app.app_core.domain.models.cafe_category_model import CafeCategoryModel


class CategoryModel(Base):
    __tablename__ = "categories"
    __table_args__ = (Index('idx_category_name', 'name'),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    cafe_associations: Mapped[List[CafeCategoryModel]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )
