import asyncio
from app.infrastructure.database import AsyncSessionLocal
from app.app_data.data import cafes_data, categories_data
from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema
from app.app_core.domain.schemas.category_schemas import CategoryCreateSchema
from app.app_core.domain.services import cafe_service, category_service
from base import SeederConfig


SEEDERS = [
    SeederConfig(
        name='cafes',
        data=cafes_data,
        schema=CafeCreateSchema,
        create_func=cafe_service.create_cafe
    ),
    SeederConfig(
        name='categories',
        data=categories_data,
        schema=CategoryCreateSchema,
        create_func=category_service.create_category
    )
]


async def seed_all():
    for seeder in SEEDERS:
        async with AsyncSessionLocal() as db:
            await seeder.seed_magic_run(db)


if __name__ == "__main__":
    asyncio.run(seed_all())
