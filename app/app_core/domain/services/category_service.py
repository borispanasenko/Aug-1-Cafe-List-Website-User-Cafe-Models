from sqlalchemy.ext.asyncio import AsyncSession
from app.app_core.domain.schemas.category_schemas import CategoryResponseSchema, CategoryCreateSchema
from app.app_core.repositories import category_repository
from app.app_core.domain.models.category_model import CategoryModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


async def create_category(db: AsyncSession, category_data: CategoryCreateSchema) -> CategoryResponseSchema | None:

    existing = await category_repository.get_category_by_name(db, category_data.name)
    if existing:
        logger.info(f"Category '{category_data.name}' already exists - quiet fallback, returning None")
        return None

    category = CategoryModel(name=category_data.name)
    created = await category_repository.add_category(db, category)
    if created is None:
        logger.warning(f"Failed to create category '{category_data.name}'")
        return None
    return CategoryResponseSchema.from_orm(created)


async def get_categories(db: AsyncSession) -> List[CategoryResponseSchema]:
    categories = await category_repository.get_all_categories(db)
    return [CategoryResponseSchema.from_orm(cat) for cat in categories]


async def get_existing_category(db: AsyncSession, category_data: CategoryCreateSchema) -> Optional[CategoryModel]:
    existing_category = await category_repository.get_category_by_name(db, category_data.name)
    if existing_category is None:
        logger.debug(f"Category '{category_data.name}' not found - quiet return None")
    return existing_category
