from sqlalchemy.ext.asyncio import AsyncSession
from app.app_core.domain.models.cafe_model import CafeModel
from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema, CafeResponseSchema, CafeUpdateSchema
from app.app_core.repositories import cafe_repository
from fastapi import HTTPException
from typing import List
import logging

logger = logging.getLogger(__name__)


async def create_cafe(db: AsyncSession, cafe_data: CafeCreateSchema) -> CafeResponseSchema:
    existing_cafe = await cafe_repository.get_cafe_by_title_and_city(db, cafe_data.title, cafe_data.city or 'Unknown')
    if existing_cafe:
        logger.info(f"Cafe '{cafe_data.title}' in '{cafe_data.city or 'Unknown'}' already exists - skipping")
        return None

    cafe = CafeModel(title=cafe_data.title, city=cafe_data.city or "Unknown",
                     description=cafe_data.description)
    cafe: CafeModel = await cafe_repository.add_cafe(db, cafe)
    return CafeResponseSchema.from_orm(cafe)


async def create_cafe_no_check(db: AsyncSession, cafe_data: CafeCreateSchema) -> CafeResponseSchema:
    cafe = CafeModel(title=cafe_data.title, city=cafe_data.city or "Unknown",
                     description=cafe_data.description)
    cafe: CafeModel = await cafe_repository.add_cafe(db, cafe)
    return CafeResponseSchema.from_orm(cafe)


async def get_or_create_cafe(db: AsyncSession, cafe_data: CafeCreateSchema) -> CafeResponseSchema:
    existing_cafe = await cafe_repository.get_cafe_by_title_and_city(db, cafe_data.title, cafe_data.city or 'Unknown')
    if existing_cafe:
        logger.info(f"Cafe '{cafe_data.title}' in '{cafe_data.city or 'Unknown'}' already exists - returning existing")
        return CafeResponseSchema.from_orm(existing_cafe)

    cafe = CafeModel(
        title=cafe_data.title,
        city=cafe_data.city or "Unknown",
        description=cafe_data.description
    )
    new_cafe = await cafe_repository.add_cafe(db, cafe)
    logger.info(f"Cafe '{new_cafe.title}' in '{new_cafe.city or 'Unknown'}' created successfully")
    return CafeResponseSchema.from_orm(new_cafe)


async def get_all_cafes(db: AsyncSession, skip: int = 0, limit: int = 30) -> List[CafeResponseSchema]:
    cafes = await cafe_repository.get_all_cafes(db, skip, limit)
    return [CafeResponseSchema.from_orm(cafe) for cafe in cafes]


async def get_cafe(db: AsyncSession, cafe_id: int) -> CafeResponseSchema | None:
    cafe = await cafe_repository.get_cafe_by_id(db, cafe_id)
    if not cafe:
        return None
    return CafeResponseSchema.from_orm(cafe)


async def update_cafe(db: AsyncSession, cafe_id: int, cafe_data: CafeUpdateSchema) -> CafeResponseSchema | None:
    cafe = await cafe_repository.get_cafe_by_id(db, cafe_id)
    if not cafe:
        return None

    if cafe_data.title is not None:
        cafe.title = cafe_data.title
    if cafe_data.city is not None:
        cafe.city = cafe_data.city
    if cafe_data.description is not None:
        cafe.description = cafe_data.description

    updated_cafe = await cafe_repository.update_existing_cafe(db, cafe)
    return CafeResponseSchema.from_orm(updated_cafe)


async def get_cafe_by_tc(db: AsyncSession, cafe_data: CafeCreateSchema) -> CafeResponseSchema | None:
    cafe = await cafe_repository.get_cafe_by_title_and_city_in_load(db, cafe_data.title, cafe_data.city or 'Unknown')
    return cafe
