from __future__ import annotations
from typing import TYPE_CHECKING
from app.infrastructure.database import Base
from sqlalchemy import Index, UniqueConstraint, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from app.app_core.domain.models.cafe_model import CafeModel
    from app.app_core.domain.models.category_model import CategoryModel


class CafeCategoryModel(Base):
    __tablename__ = "cafe_categories"
    __table_args__ = (
        UniqueConstraint("cafe_id", "category_id", name="uq_cafe_category"),
        Index('idx_cafe_category_cafe_id', 'cafe_id'),
        Index('idx_cafe_category_category_id', 'category_id'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    is_best: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cafe: Mapped[CafeModel] = relationship(back_populates="category_associations")
    category: Mapped[CategoryModel] = relationship(back_populates="cafe_associations")

