from sqlalchemy.orm import Session
from app.app_core.domain.schemas.category_schemas import CategoryResponseSchema, CategoryCreateSchema
from app.app_core.repositories import category_repository
from app.app_core.domain.models.category_model import CategoryModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def create_category(db: Session, category_data: CategoryCreateSchema) -> CategoryResponseSchema | None:

    existing = category_repository.get_category_by_name(db, category_data.name)
    if existing:
        logger.info(f"Category '{category_data.name}' already exists - quiet fallback, returning None")
        return None

    category = CategoryModel(name=category_data.name)
    created = category_repository.add_category(db, category)
    if created is None:
        logger.warning(f"Failed to create category '{category_data.name}'")
        return None
    return CategoryResponseSchema.from_orm(created)


def get_categories(db: Session) -> List[CategoryResponseSchema]:
    categories = category_repository.get_all_categories(db)
    return [CategoryResponseSchema.from_orm(cat) for cat in categories]


def get_existing_category(db: Session, category_data: CategoryCreateSchema) -> Optional[CategoryModel]:
    existing_category = category_repository.get_category_by_name(db, category_data.name)
    if existing_category is None:
        logger.debug(f"Category '{category_data.name}' not found - quiet return None")
    return existing_category
