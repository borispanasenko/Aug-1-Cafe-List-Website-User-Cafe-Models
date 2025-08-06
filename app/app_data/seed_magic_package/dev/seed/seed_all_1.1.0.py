import asyncio
from app.infrastructure.database import AsyncSessionLocal
from app.app_data.data import cafes_data, categories_data
from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema
from app.app_core.domain.schemas.category_schemas import CategoryCreateSchema
from app.app_core.domain.services import cafe_service, category_service
from base import SeederConfig
from app.app_core.repositories import cafe_repository, category_repository
from app.app_core.domain.models.cafe_category_model import CafeCategoryModel
from app.app_core.domain.models.cafe_model import CafeModel
from app.app_core.domain.models.category_model import CategoryModel
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)


async def update_cafe_seed(db: AsyncSessionLocal, existing: CafeModel, entity: CafeCreateSchema) -> bool:
    updated = False
    if existing.description != entity.description:
        existing.description = entity.description
        updated = True
    if existing.image_url != entity.image_url:
        existing.image_url = entity.image_url
        updated = True
    if updated:
        await cafe_repository.update_existing_cafe(db, existing)
    return updated


async def add_associations(db: AsyncSessionLocal, entity: CafeCreateSchema) -> bool | None:
    cafe = await cafe_repository.get_cafe_by_title_and_city(db, entity.title, entity.city or 'Unknown')
    if not cafe:
        logger.warning(f"Cafe not found for associations: {entity.title}")
        return None

    categories_result = await db.execute(select(CategoryModel))
    categories = {c.name: c.id for c in categories_result.scalars().all()}

    if entity.best_for not in categories:
        logger.error(f"Invalid best_for '{entity.best_for}' for {entity.title}")
        return None
    invalid_cats = [cat for cat in entity.also_good_for if cat not in categories]
    if invalid_cats:
        logger.error(f"Invalid also_good_for {invalid_cats} for {entity.title}")
        return None

    unique_categories = {entity.best_for} | set(entity.also_good_for)
    desired_category_ids = {categories[cat_name] for cat_name in unique_categories}
    best_for_id = categories[entity.best_for]

    assocs_result = await db.execute(select(CafeCategoryModel).filter_by(cafe_id=cafe.id))
    existing_assocs = {assoc.category_id: assoc for assoc in assocs_result.scalars().all()}
    current_assoc_ids = set(existing_assocs.keys())

    added = 0
    updated = 0
    removed = 0
    new_assocs = []
    for cat_id in desired_category_ids:
        is_best = (cat_id == best_for_id)
        if cat_id in existing_assocs:
            assoc = existing_assocs[cat_id]
            if assoc.is_best != is_best:
                assoc.is_best = is_best
                updated += 1
        else:
            new_assocs.append(CafeCategoryModel(cafe_id=cafe.id, category_id=cat_id, is_best=is_best))
            added += 1
    for cat_id in current_assoc_ids - desired_category_ids:
        db.delete(existing_assocs[cat_id])
        removed += 1

    if added or updated or removed:
        if new_assocs:
            db.add_all(new_assocs)
        await db.commit()
        logger.info(f"Associations for {entity.title}: added={added}, updated={updated}, removed={removed}")
        return True
    return None


SEEDERS = [
    SeederConfig(
        name='categories',
        data=categories_data,
        schema=CategoryCreateSchema,
        create_func=category_service.create_category,
        get_existing_func=category_service.get_existing_category
    ),
    SeederConfig(
        name='cafes',
        data=cafes_data,
        schema=CafeCreateSchema,
        create_func=cafe_service.create_cafe,
        get_existing_func=cafe_service.get_existing_cafe,
        update_func=update_cafe_seed
    ),
    SeederConfig(
        name='cafe_categories',
        data=cafes_data,
        schema=CafeCreateSchema,
        create_func=add_associations,
        get_existing_func=None
    )
]


async def seed_all():
    for seeder in SEEDERS:
        async with AsyncSessionLocal() as db:
            await seeder.seed_magic_run(db)


if __name__ == "__main__":
    asyncio.run(seed_all())
