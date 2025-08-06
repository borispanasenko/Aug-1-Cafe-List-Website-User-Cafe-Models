import logging
from typing import List, Type, TypeVar, Callable, Optional, Awaitable
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


Schema = TypeVar('Schema', bound=BaseModel)


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


async def validate(raw_data: List[dict], schema: Type[Schema]) -> List[Schema]:
    validated = []
    for i, entity in enumerate(raw_data):
        try:
            validated.append(schema(**entity))
        except ValidationError as e:
            logger.error(f'Validation error at item {i}: {e}')
    return validated


async def run_seed(
        db: AsyncSession,
        raw_data: List[dict],
        schema: Type[Schema],
        # Dependent on service functions
        get_existing_func: Optional[Callable[[AsyncSession, Schema], Awaitable[Optional[object]]]] = None,
        create_func: Optional[Callable[[AsyncSession, Schema], Awaitable[object]]] = None,
        update_func: Optional[Callable[[AsyncSession, object, Schema], Awaitable[bool]]] = None
):
    validated_data = await validate(raw_data, schema)
    created_count = 0
    updated_count = 0

    for entity in validated_data:
        existing = None
        if get_existing_func:
            existing = await get_existing_func(db, entity)

        if existing:
            if update_func:
                try:
                    updated = await update_func(db, existing, entity)
                    if updated:
                        # db commits must be handled in respective repos
                        updated_count += 1
                        logger.info(f"Updated: {entity}")
                except (IntegrityError, HTTPException) as e:
                    logger.error(f"Error while updating: {e}")
            else:
                logger.info(f"Skipped (exists, no update): {entity}")

        else:
            try:
                result = await create_func(db, entity)
                if result is not None:
                    created_count += 1
                    logger.info(f"Created: {entity}")
                else:
                    logger.info(f"Skipped (create returned None): {entity}")
            except (IntegrityError, HTTPException) as e:
                logger.error(f"Error while creating: {e}")
                logger.info(f"Skipped (duplicate or error): {entity}")

    logger.info(f"Seed completed. Created: {created_count}, Updated: {updated_count}")
