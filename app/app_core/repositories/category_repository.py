from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.app_core.domain.models.category_model import CategoryModel
from sqlalchemy.future import select
import logging


logger = logging.getLogger(__name__)


def add_category(db: Session, category: CategoryModel) -> CategoryModel:
    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Integrity error adding category '{category.name}': {str(e)}")
        return None
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f'DB error adding category: {str(e)}')
        raise HTTPException(status_code=500, detail='Database error') from e


def get_all_categories(db: Session) -> List[CategoryModel]:
    try:
        result = db.execute(select(CategoryModel))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f'DB error fetching all categories: {str(e)}')
        return []


def get_category_by_name(db: Session, name: str) -> Optional[CategoryModel]:
    try:
        return db.query(CategoryModel).filter_by(name=name).first()
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching category by name '{name}': {str(e)}")
        return None
