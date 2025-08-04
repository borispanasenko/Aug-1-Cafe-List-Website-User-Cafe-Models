from pydantic import BaseModel, model_validator
from app.app_core.domain.schemas.category_schemas import *
from typing import List, Optional


class CafeBaseSchema(BaseModel):
    title: str
    city: str
    description: Optional[str] = None


class CafeCreateSchema(CafeBaseSchema):
    ...


class CafeUpdateSchema(CafeBaseSchema):
    title: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None


class CafeResponseSchema(CafeBaseSchema):
    id: int
    image_url: Optional[str] = None
    average_rating: float = 0.0
    best_for: Optional[CategoryResponseSchema] = None
    also_good_for: List[CategoryResponseSchema] = []

    class Config:
        from_attributes = True
