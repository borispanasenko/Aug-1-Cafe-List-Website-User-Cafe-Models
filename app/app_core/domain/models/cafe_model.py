from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

if TYPE_CHECKING:
    from app.app_core.domain.models.category_model import CategoryModel
    from app.app_core.domain.models.cafe_category_model import CafeCategoryModel
    from app.app_core.domain.models.review_model import ReviewModel


class CafeModel(Base):
    __tablename__ = 'cafes'
    __table_args__ = (
        UniqueConstraint("title", "city", name="uq_cafe_title_city"),
        Index('idx_cafe_city', 'city'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    category_associations: Mapped[List[CafeCategoryModel]] = relationship(
        back_populates="cafe", cascade="all, delete-orphan"
    )
    reviews: Mapped[List[ReviewModel]] = relationship(
        back_populates="cafe", cascade="all, delete-orphan"
    )

    @property
    def best_for(self) -> Optional[CategoryModel]:
        for assoc in self.category_associations:
            if assoc.is_best:
                return assoc.category
        return None

    @property
    def also_good_for(self) -> List[CategoryModel]:
        return [assoc.category for assoc in self.category_associations if not assoc.is_best]

    @property
    def average_rating(self) -> float:
        if not self.reviews:
            return 0.0
        total_rating = sum(review.rating for review in self.reviews)
        return total_rating / len(self.reviews)
