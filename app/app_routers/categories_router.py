# –––––––––––––––––– IMPORTS –––––––––––––––––– #

from fastapi import APIRouter, Depends
from app.app_core.domain.schemas.category_schemas import CategoryResponseSchema
from sqlalchemy.orm import Session
from app.app_dependencies.dependencies import get_db
from app.app_core.domain.services import category_service
from typing import List


# –––––––––––––––––– ROUTER –––––––––––––––––– #

router = APIRouter(prefix='/categories', tags=['categories'])


# –––––––––––––––––– ROUTES –––––––––––––––––– #

@router.get('/', response_model=List[CategoryResponseSchema])
def get_categories(db: Session = Depends(get_db)):
    categories = category_service.get_categories(db)
    return categories
