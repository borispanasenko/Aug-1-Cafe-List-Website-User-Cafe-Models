# –––––––––––––––––– IMPORTS –––––––––––––––––– #

from fastapi import APIRouter, Depends, HTTPException, Query
from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema, CafeResponseSchema, CafeUpdateSchema
from app.app_core.domain.models.user_model import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.app_dependencies.dependencies import get_db
from app.app_core.domain.services import cafe_service
from app.infrastructure.auth_backend import current_superuser
from typing import List

# –––––––––––––––––– ROUTER –––––––––––––––––– #

router = APIRouter(prefix='/cafes', tags=['cafes'])


# –––––––––––––––––– ROUTES –––––––––––––––––– #

@router.post('/', response_model=CafeResponseSchema)
async def create_new_cafe(cafe_data: CafeCreateSchema, db: AsyncSession = Depends(get_db),
                          _user: UserModel = Depends(current_superuser)):
    return await cafe_service.create_cafe(db, cafe_data)


@router.get('/', response_model=List[CafeResponseSchema])
async def read_all_cafes(db: AsyncSession = Depends(get_db), skip: int = Query(0, ge=0)):
    limit: int = 30
    return await cafe_service.get_all_cafes(db, skip, limit)


@router.put('/{cafe_id}', response_model=CafeResponseSchema)
async def update_existing_cafe(cafe_id: int, cafe_data: CafeUpdateSchema, db: AsyncSession = Depends(get_db),
                               _user: UserModel = Depends(current_superuser)):
    updated_cafe = await cafe_service.update_cafe(db, cafe_id, cafe_data)
    if not updated_cafe:
        raise HTTPException(status_code=404, detail='Cafe not found')
    return updated_cafe


@router.get('/cafes/{cafe_id}', response_model=CafeResponseSchema)
async def read_cafe(cafe_id: int, db: AsyncSession = Depends(get_db)):
    # _user: UserModel = Depends(current_user)
    cafe = await cafe_service.get_cafe(db, cafe_id)
    if not cafe:
        raise HTTPException(status_code=404, detail='Cafe not found')
    return cafe
