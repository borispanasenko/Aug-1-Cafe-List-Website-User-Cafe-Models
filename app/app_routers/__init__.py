# –––––––––––––––––– IMPORTS –––––––––––––––––– #

from fastapi import APIRouter
from app.app_routers import auth_router, users_router, cafes_router, categories_router

# ––––––––––––––––––––––––– ROUTER ––––––––––––––––––––––––– #

router = APIRouter()
router.include_router(auth_router.router)
router.include_router(users_router.router)
router.include_router(cafes_router.router)
router.include_router(categories_router.router)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––– #
# from sqlalchemy.orm import Session
# from app.app_dependencies.core_dependencies import get_db
# from fastapi import APIRouter, Depends, HTTPException, Query
# from app.app_core.domain.schemas.user_schemas import UserCreateSchema, UserReadSchema, UserUpdateSchema
# from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema, CafeUpdateSchema, CafeResponseSchema
# from app.app_core.domain.services import cafe_service
#
# from app.app_core.domain.schemas.category_schemas import CategoryResponseSchema
# from app.app_core.domain.services import category_service
# from typing import List


# # –––––––––––––––––– USER AUTH IMPORTS –––––––––––––––––– #
#
# from app.app_core.domain.models import UserModel
# from app.auth import auth_backend, fastapi_users, current_user, current_superuser


# # ––––––––––––––––––––––––– FASTAPI USER ROUTERS ––––––––––––––––––––––––– #
#
# router.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix="/auth/jwt",
#     tags=["auth"]
# )
#
# router.include_router(
#     fastapi_users.get_register_router(UserReadSchema, UserCreateSchema),
#     prefix="/auth",
#     tags=["auth"]
# )
# router.include_router(
#     fastapi_users.get_users_router(UserReadSchema, UserUpdateSchema),
#     prefix="/users",
#     tags=["users"]
# )
#
#
# # ––––––––––––––––––––––––– CAFE ROUTES ––––––––––––––––––––––––– #
#
# @router.post('/cafes', response_model=CafeResponseSchema)
# def create_new_cafe(cafe_data: CafeCreateSchema, db: Session = Depends(get_db),
#                     _user: UserModel = Depends(current_superuser)):
#     return cafe_service.create_cafe(db, cafe_data)
#
#
# @router.get('/cafes', response_model=List[CafeResponseSchema])
# def read_all_cafes(db: Session = Depends(get_db), skip: int = Query(0, ge=0)):
#     limit: int = 30
#     return cafe_service.get_all_cafes(db, skip, limit)
#
#
# @router.put('/cafes/{cafe_id}', response_model=CafeResponseSchema)
# def update_existing_cafe(cafe_id: int, cafe_data: CafeUpdateSchema, db: Session = Depends(get_db),
#                          _user: UserModel = Depends(current_superuser)):
#     updated_cafe = cafe_service.update_cafe(db, cafe_id, cafe_data)
#     if not updated_cafe:
#         raise HTTPException(status_code=404, detail='Cafe not found')
#     return updated_cafe
#
#
# @router.get('/cafes/{cafe_id}', response_model=CafeResponseSchema)
# def read_cafe(cafe_id: int, db: Session = Depends(get_db),
#               _user: UserModel = Depends(current_user)):
#     cafe = cafe_service.get_cafe(db, cafe_id)
#     if not cafe:
#         raise HTTPException(status_code=404, detail='Cafe not found')
#     return cafe
#
#
# # ––––––––––––––––––––––––– CATEGORY ROUTES ––––––––––––––––––––––––– #
#
# @router.get('/categories', response_model=List[CategoryResponseSchema])
# def get_categories(db: Session = Depends(get_db)):
#     categories = category_service.get_categories(db)
#     return categories
