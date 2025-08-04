import logging
from typing import List, Type, TypeVar, Callable, Optional
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


Schema = TypeVar('Schema', bound=BaseModel)


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


def validate(raw_data: List[dict], schema: Type[Schema]) -> List[Schema]:
    validated = []
    for i, entity in enumerate(raw_data):
        try:
            validated.append(schema(**entity))
        except ValidationError as e:
            logger.error(f'Validation error at item {i}: {e}')
    return validated


def run_seed(
        db: Session,
        raw_data: List[dict],
        schema: Type[Schema],
        get_existing_func: Callable[[Session, Schema], Optional[object]],
        create_func: Callable[[Session, Schema], object],
        update_func: Optional[Callable[[Session, object, Schema], bool]] = None
):
    validated_data = validate(raw_data, schema)
    created_count = 0
    updated_count = 0

    for entity in validated_data:
        existing = get_existing_func(db, entity)
        if existing:
            if update_func:
                try:
                    updated = update_func(db, existing, entity)
                    if updated:
                        db.commit()
                        updated_count += 1
                        logger.info(f"Updated: {entity}")
                except IntegrityError as e:
                    db.rollback()
                    logger.error(f"Integrity error while updating: {e}")
        else:
            try:
                create_func(db, entity)
                created_count += 1
                logger.info(f"Created: {entity}")
            except IntegrityError as e:
                db.rollback()
                logger.error(f"Integrity error while creating: {e}")

    logger.info(f"Seed completed. Created: {created_count}, Updated: {updated_count}")
