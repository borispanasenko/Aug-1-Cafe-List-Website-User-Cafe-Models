# –––––––––––––––––– IMPORTS –––––––––––––––––– #

from fastapi import APIRouter, Depends
from app.app_core.domain.models.category_model import CategoryModel
from app.app_core.domain.schemas.category_schemas import CategoryResponseSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.app_dependencies.dependencies import get_db
from app.app_core.domain.services import category_service
from typing import List


# –––––––––––––––––– ROUTER –––––––––––––––––– #

router = APIRouter(prefix='/categories', tags=['categories'])


# –––––––––––––––––– ROUTES –––––––––––––––––– #

@router.get('/', response_model=List[CategoryResponseSchema])
async def get_categories(db: AsyncSession = Depends(get_db)):
    categories: List[CategoryModel] = await category_service.get_categories(db)
    return [CategoryResponseSchema.from_orm(cat) for cat in categories]
