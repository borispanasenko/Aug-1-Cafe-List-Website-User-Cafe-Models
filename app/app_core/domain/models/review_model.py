from __future__ import annotations
from typing import TYPE_CHECKING
from app.infrastructure.database import Base
from sqlalchemy import Index, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


if TYPE_CHECKING:
    from app.app_core.domain.models.cafe_model import CafeModel


class ReviewModel(Base):
    __tablename__ = 'reviews'
    __table_args__ = (
        Index('idx_review_cafe_id', 'cafe_id'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafes.id'), nullable=False)
    user_id: Mapped[PG_UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    cafe: Mapped[CafeModel] = relationship(back_populates='reviews')
