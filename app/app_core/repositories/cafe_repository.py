from sqlalchemy.orm import Session
from app.app_core.domain.models.cafe_model import CafeModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.future import select
from typing import List


def add_cafe(db: Session, cafe: CafeModel) -> CafeModel:
    try:
        db.add(cafe)
        db.commit()
        db.refresh(cafe)
        return cafe
    except IntegrityError as e:
        db.rollback()
        if 'unique constraint' in str(e.orig):
            raise HTTPException(status_code=409, detail='Cafe with this name and location already exists')
        else:
            raise HTTPException(status_code=500, detail='Database integrity error')


def get_all_cafes(db: Session, skip: int = 0, limit: int = 30) -> List[CafeModel]:
    try:
        result = db.execute(select(CafeModel).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail='Database error while fetching cafes') from e


def get_cafe_by_id(db: Session, cafe_id: int) -> CafeModel | None:
    try:
        return db.query(CafeModel).filter(CafeModel.id == cafe_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail='Database error while fetching cafe by ID') from e


def get_cafe_by_title_and_city(db: Session, title: str, city: str) -> CafeModel | None:
    try:
        return db.query(CafeModel).filter(
            CafeModel.name == title,
            CafeModel.location == city,
        ).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail='Database error while fetching cafe by title and city') from e


def update_existing_cafe(db: Session, cafe: CafeModel) -> CafeModel:
    try:
        db.commit()
        db.refresh(cafe)
        return cafe
    except IntegrityError as e:
        db.rollback()
        if 'unique constraint' in str(e.orig):
            raise HTTPException(status_code=409, detail='Update failed: duplicate name and location')
        else:
            raise HTTPException(status_code=500, detail='Database integrity error')
