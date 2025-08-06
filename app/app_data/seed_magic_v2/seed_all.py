import asyncio
from typing import Optional, Callable, Awaitable
import logging

from app.infrastructure.database import AsyncSessionLocal
from app.app_data.data import cafes_data, categories_data
from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema
from app.app_core.domain.schemas.category_schemas import CategoryCreateSchema
from app.app_core.domain.services import cafe_service, category_service
from base import SeederConfig
from app.app_core.repositories import cafe_repository
from app.app_core.domain.models.cafe_category_model import CafeCategoryModel
from app.app_core.domain.models.cafe_model import CafeModel
from app.app_core.domain.models.category_model import CategoryModel
from sqlalchemy import select

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def update_cafe_seed(db: AsyncSessionLocal, existing: CafeModel, entity: CafeCreateSchema) -> bool:
    updated = False
    for attr in ("description", "image_url"):
        new_val = getattr(entity, attr)
        if getattr(existing, attr) != new_val:
            setattr(existing, attr, new_val)
            updated = True
    if updated:
        await cafe_repository.update_existing_cafe(db, existing)
    return updated


def make_add_associations() -> Callable[[AsyncSessionLocal, CafeCreateSchema], Awaitable[Optional[object]]]:
    """
    Create func that ensures cafe-category associations reflect the schema.
    Returns the cafe if any change/addition/removal occurred, otherwise None.
    """
    _categories_cache: Optional[dict[str, int]] = None

    async def add_associations(db: AsyncSessionLocal, entity: CafeCreateSchema) -> Optional[object]:
        nonlocal _categories_cache
        cafe = await cafe_repository.get_cafe_by_title_and_city(db, entity.title, entity.city or 'Unknown')
        if not cafe:
            logger.warning("Cafe not found for associations: title=%s, city=%s", entity.title, entity.city)
            logger.debug("Full entity: %s", entity.dict())
            return None

        if _categories_cache is None:
            result = await db.execute(select(CategoryModel))
            _categories_cache = {c.name: c.id for c in result.scalars().all()}

        categories = _categories_cache
        if entity.best_for not in categories:
            logger.error("Invalid best_for '%s' for %s", entity.best_for, entity.title)
            logger.debug("Full entity: %s", entity.dict())
            return None
        invalid_cats = [cat for cat in entity.also_good_for if cat not in categories]
        if invalid_cats:
            logger.error("Invalid also_good_for %s for %s", invalid_cats, entity.title)
            logger.debug("Full entity: %s", entity.dict())
            return None

        desired_category_ids = {categories[cat_name] for cat_name in {entity.best_for} | set(entity.also_good_for)}
        best_for_id = categories[entity.best_for]

        assocs_result = await db.execute(select(CafeCategoryModel).filter_by(cafe_id=cafe.id))
        existing_assocs = {assoc.category_id: assoc for assoc in assocs_result.scalars().all()}
        current_assoc_ids = set(existing_assocs.keys())

        added = updated = removed = 0
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
            logger.info("Associations for %s: added=%d, updated=%d, removed=%d", entity.title, added, updated, removed)
            return cafe
        return None

    return add_associations


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
        create_func=cafe_service.create_cafe_no_check,
        get_existing_func=cafe_service.get_cafe_by_tc,
        update_func=update_cafe_seed
    ),
    SeederConfig(
        name='cafe_categories',
        data=cafes_data,
        schema=CafeCreateSchema,
        create_func=make_add_associations(),
        get_existing_func=None
    )
]


async def seed_all():
    for seeder in SEEDERS:
        async with AsyncSessionLocal() as db:
            try:
                await seeder.seed_magic_run(db)
            except Exception as e:
                logger.error("Seeder %s failed: %s", seeder.name, e)
                # decide: break or continue
                break

if __name__ == "__main__":
    asyncio.run(seed_all())
