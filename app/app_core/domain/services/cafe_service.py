from sqlalchemy.orm import Session
from app.app_core.domain.models.cafe_model import CafeModel
from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema, CafeResponseSchema, CafeUpdateSchema
from app.app_core.repositories import cafe_repository
from fastapi import HTTPException
from typing import List


def create_cafe(db: Session, cafe_data: CafeCreateSchema) -> CafeResponseSchema:
    existing_cafe = cafe_repository.get_cafe_by_title_and_city(db, cafe_data.title, cafe_data.city or 'Unknown')
    if existing_cafe:
        raise HTTPException(
            status_code=409,
            detail=f"Cafe with title '{cafe_data.title}' in city '{cafe_data.city or 'Unknown'}' already exists"
        )

    cafe = CafeModel(title=cafe_data.title, city=cafe_data.city or "Unknown",
                     description=cafe_data.description)
    cafe = cafe_repository.add_cafe(db, cafe)
    return CafeResponseSchema.from_orm(cafe)


def get_all_cafes(db: Session, skip: int = 0, limit: int = 30) -> List[CafeResponseSchema]:
    cafes = cafe_repository.get_all_cafes(db, skip, limit)
    return [CafeResponseSchema.from_orm(cafe) for cafe in cafes]


def get_cafe(db: Session, cafe_id: int) -> CafeResponseSchema | None:
    cafe = cafe_repository.get_cafe_by_id(db, cafe_id)
    return CafeResponseSchema.from_orm(cafe)


def update_cafe(db: Session, cafe_id: int, cafe_data: CafeUpdateSchema) -> CafeResponseSchema | None:
    cafe = cafe_repository.get_cafe_by_id(db, cafe_id)
    if not cafe:
        return None

    if cafe_data.title is not None:
        cafe.title = cafe_data.title
    if cafe_data.city is not None:
        cafe.city = cafe_data.city
    if cafe_data.description is not None:
        cafe.description = cafe_data.description

    updated_cafe = cafe_repository.update_existing_cafe(db, cafe)
    return CafeResponseSchema.from_orm(updated_cafe)
