import logging
from typing import List, Type, TypeVar, Callable, Optional, Awaitable, Protocol
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

Schema = TypeVar('Schema', bound=BaseModel)


# Протоколы для сигнатур (самодокументирующиеся)
class CreateFunc(Protocol):
    async def __call__(self, db: AsyncSession, model: Schema) -> Optional[object]:
        ...


class GetExistingFunc(Protocol):
    async def __call__(self, db: AsyncSession, model: Schema) -> Optional[object]:
        ...


class UpdateFunc(Protocol):
    async def __call__(self, db: AsyncSession, existing: object, model: Schema) -> bool:
        ...


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def validate(raw_data: List[dict], schema: Type[Schema]) -> List[Schema]:
    validated: List[Schema] = []
    for i, entity in enumerate(raw_data):
        validated.append(schema(**entity))
    return validated


async def run_seed(
        db: AsyncSession,
        raw_data: List[dict],
        schema: Type[Schema],
        create_func: CreateFunc,
        get_existing_func: Optional[GetExistingFunc] = None,
        update_func: Optional[UpdateFunc] = None,
):
    validated_data = validate(raw_data, schema)
    created_count = 0
    updated_count = 0

    for entity in validated_data:
        existing = None
        if get_existing_func:
            existing = await get_existing_func(db, entity)

        if existing:
            if update_func:
                updated = await update_func(db, existing, entity)
                if updated:
                    updated_count += 1
                    logger.info("Updated: %s", _summarize(entity))
            else:
                logger.info("Skipped (exists, no update func): %s", _summarize(entity))
        else:
            result = await create_func(db, entity)
            if result is not None:
                created_count += 1
                logger.info("Created: %s", _summarize(entity))
            else:
                logger.info("Skipped (create returned None): %s", _summarize(entity))

    logger.info("Seed completed. Created: %d, Updated: %d", created_count, updated_count)


def _summarize(entity: BaseModel) -> str:
    # Пример: взять первичный ключ или пару полей для читаемого лога
    if hasattr(entity, 'id'):
        return f"{entity.__class__.__name__}(id={getattr(entity, 'id')})"
    # fallback: ограниченная строка
    repr_str = str(entity.dict())
    return repr_str if len(repr_str) <= 200 else repr_str[:200] + "…"
