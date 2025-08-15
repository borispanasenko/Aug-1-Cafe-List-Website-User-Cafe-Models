# –––––––––––––––––– IMPORTS –––––––––––––––––– #

from fastapi import APIRouter, Depends, HTTPException, Query
from app.app_core.domain.models.cafe_model import CafeModel
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

@router.post('', response_model=CafeResponseSchema)
@router.post('/', include_in_schema=False)
async def create_new_cafe(cafe_data: CafeCreateSchema, db: AsyncSession = Depends(get_db),
                          _user: UserModel = Depends(current_superuser)):
    cafe: CafeModel = await cafe_service.create_cafe(db, cafe_data)
    return CafeResponseSchema.from_orm(cafe)


@router.get('', response_model=List[CafeResponseSchema])
@router.get('/', include_in_schema=False)
async def read_all_cafes(db: AsyncSession = Depends(get_db), skip: int = Query(0, ge=0)):
    limit: int = 30
    cafes: List[CafeModel] = await cafe_service.get_all_cafes(db, skip, limit)
    return [CafeResponseSchema.from_orm(cafe) for cafe in cafes]


@router.put('/{cafe_id}', response_model=CafeResponseSchema)
async def update_existing_cafe(cafe_id: int, cafe_data: CafeUpdateSchema, db: AsyncSession = Depends(get_db),
                               _user: UserModel = Depends(current_superuser)):
    updated_cafe: CafeModel | None = await cafe_service.update_cafe(db, cafe_id, cafe_data)
    if not updated_cafe:
        raise HTTPException(status_code=404, detail='Cafe not found')
    return CafeResponseSchema.from_orm(updated_cafe)


@router.get('/{cafe_id}', response_model=CafeResponseSchema)
async def read_cafe(cafe_id: int, db: AsyncSession = Depends(get_db)):
    cafe: CafeModel | None = await cafe_service.get_cafe(db, cafe_id)
    if not cafe:
        raise HTTPException(status_code=404, detail='Cafe not found')
    return CafeResponseSchema.from_orm(cafe)
