from sqlalchemy.ext.asyncio import AsyncSession
from app.app_core.domain.models.category_model import CategoryModel
from app.app_core.repositories import category_repository
from app.app_core.domain.schemas.category_schemas import CategoryCreateSchema
from typing import List
import logging

logger = logging.getLogger(__name__)


async def create_category(db: AsyncSession, category_data: CategoryCreateSchema) -> CategoryModel:
    existing = await category_repository.get_category_by_name(db, category_data.name)
    if existing:
        logger.info(f"Category '{category_data.name}' already exists - skipping")
        return existing
    category = CategoryModel(name=category_data.name)
    return await category_repository.add_category(db, category)


async def get_categories(db: AsyncSession) -> List[CategoryModel]:
    return await category_repository.get_all_categories(db)


async def get_existing_category(db: AsyncSession, category_data: CategoryCreateSchema) -> CategoryModel | None:
    return await category_repository.get_category_by_name(db, category_data.name)
