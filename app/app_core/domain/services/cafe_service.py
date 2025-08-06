from sqlalchemy.ext.asyncio import AsyncSession
from app.app_core.domain.models.cafe_model import CafeModel
from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema, CafeUpdateSchema  # Только для input
from app.app_core.repositories import cafe_repository
from typing import List
import logging

logger = logging.getLogger(__name__)


async def create_cafe(db: AsyncSession, cafe_data: CafeCreateSchema, check_existing: bool = True) -> CafeModel:
    if check_existing:
        existing = await cafe_repository.get_cafe_by_title_and_city(db, cafe_data.title, cafe_data.city or 'Unknown')
        if existing:
            logger.info(
                f"Cafe '{cafe_data.title}' in '{cafe_data.city or 'Unknown'}' already exists - returning existing")
            return existing
    cafe = CafeModel(
        title=cafe_data.title,
        city=cafe_data.city or "Unknown",
        description=cafe_data.description
    )
    created = await cafe_repository.add_cafe(db, cafe)
    logger.info(f"Cafe '{created.title}' in '{created.city}' created successfully")
    return created


async def get_all_cafes(db: AsyncSession, skip: int = 0, limit: int = 30) -> List[CafeModel]:
    return await cafe_repository.get_all_cafes(db, skip, limit)


async def get_cafe(db: AsyncSession, cafe_id: int) -> CafeModel | None:
    return await cafe_repository.get_cafe_by_id(db, cafe_id)


async def update_cafe(db: AsyncSession, cafe_id: int, cafe_data: CafeUpdateSchema) -> CafeModel | None:
    cafe = await cafe_repository.get_cafe_by_id(db, cafe_id)
    if not cafe:
        return None
    if cafe_data.title is not None:
        cafe.title = cafe_data.title
    if cafe_data.city is not None:
        cafe.city = cafe_data.city
    if cafe_data.description is not None:
        cafe.description = cafe_data.description
    return await cafe_repository.update_existing_cafe(db, cafe)


async def get_cafe_by_tc(db: AsyncSession, cafe_data: CafeCreateSchema) -> CafeModel | None:
    return await cafe_repository.get_cafe_by_title_and_city(db, cafe_data.title, cafe_data.city or 'Unknown')
