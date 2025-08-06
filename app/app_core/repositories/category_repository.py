from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.app_core.domain.models.category_model import CategoryModel
from sqlalchemy.future import select
import logging


logger = logging.getLogger(__name__)


async def add_category(db: AsyncSession, category: CategoryModel) -> Optional[CategoryModel]:
    try:
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category
    except IntegrityError as e:
        # await db.rollback()
        # logger.warning(f"Integrity error adding category '{category.name}': {str(e)}")
        # return None
        ...
    except SQLAlchemyError as e:
        # await db.rollback()
        # logger.error(f'DB error adding category: {str(e)}')
        # raise HTTPException(status_code=500, detail='Database error') from e
        ...


async def get_all_categories(db: AsyncSession) -> List[CategoryModel]:
    try:
        result = await db.execute(select(CategoryModel))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f'DB error fetching all categories: {str(e)}')
        return []


async def get_category_by_name(db: AsyncSession, name: str) -> Optional[CategoryModel]:
    try:
        result = await db.execute(select(CategoryModel).where(CategoryModel.name == name))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching category by name '{name}': {str(e)}")
        return None
