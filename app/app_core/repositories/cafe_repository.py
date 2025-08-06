from sqlalchemy.ext.asyncio import AsyncSession
from app.app_core.domain.models.cafe_model import CafeModel
from app.app_core.domain.models.cafe_category_model import CafeCategoryModel
from app.app_core.domain.models.review_model import ReviewModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from sqlalchemy.future import select
from typing import List


async def add_cafe(db: AsyncSession, cafe: CafeModel) -> CafeModel:
    try:
        db.add(cafe)
        await db.commit()
        await db.refresh(cafe)

        result = await db.execute(
            select(CafeModel).options
            (
                selectinload(CafeModel.category_associations).selectinload(CafeCategoryModel.category),
                selectinload(CafeModel.reviews)
            ).where(CafeModel.id == cafe.id)
        )
        cafe = result.scalar_one()
        return cafe
    except IntegrityError as e:
        await db.rollback()
        if 'unique constraint' in str(e.orig):
            raise HTTPException(status_code=409, detail='Cafe with this name and location already exists')
        else:
            raise HTTPException(status_code=500, detail='Database integrity error')


async def get_all_cafes(db: AsyncSession, skip: int = 0, limit: int = 30) -> List[CafeModel]:
    try:
        result = await db.execute(select(CafeModel).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail='Database error while fetching cafes') from e


async def get_cafe_by_id(db: AsyncSession, cafe_id: int) -> CafeModel | None:
    try:
        result = await db.execute(select(CafeModel).where(CafeModel.id == cafe_id))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail='Database error while fetching cafe by ID') from e


async def get_cafe_by_title_and_city(db: AsyncSession, title: str, city: str) -> CafeModel | None:
    try:
        result = await db.execute(
            select(CafeModel).where(
                CafeModel.title == title,
                CafeModel.city == city,))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail='Database error while fetching cafe by title and city') from e


async def get_cafe_by_title_and_city_in_load(
    db: AsyncSession,
    title: str,
    city: str,
) -> CafeModel | None:
    try:
        result = await db.execute(
            select(CafeModel)
            .options(
                selectinload(CafeModel.category_associations).selectinload(CafeCategoryModel.category),
                selectinload(CafeModel.reviews)
            )
            .where(
                CafeModel.title == title,
                CafeModel.city == city,
            )
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail='Database error while fetching cafe by title and city') from e


async def update_existing_cafe(db: AsyncSession, cafe: CafeModel) -> CafeModel:
    try:
        await db.commit()
        await db.refresh(cafe)
        result = await db.execute(
            select(CafeModel).options(
                selectinload(CafeModel.category_associations).selectinload(CafeCategoryModel.category),
                selectinload(CafeModel.reviews)
            ).where(CafeModel.id == cafe.id)
        )
        cafe = result.scalar_one()
        return cafe
    except IntegrityError as e:
        await db.rollback()
        if 'unique constraint' in str(e.orig):
            raise HTTPException(status_code=409, detail='Update failed: duplicate name and location')
        else:
            raise HTTPException(status_code=500, detail='Database integrity error')
