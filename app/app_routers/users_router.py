# –––––––––––––––––– USER IMPORTS –––––––––––––––––– #

from fastapi import APIRouter
from app.infrastructure.auth_backend import fastapi_users
from app.app_core.domain.schemas.user_schemas import UserReadSchema, UserUpdateSchema


# ––––––––––––––––––––––––– USER ROUTER ––––––––––––––––––––––––– #

router = APIRouter(prefix='/users', tags=['users'])

router.include_router(
    fastapi_users.get_users_router(UserReadSchema, UserUpdateSchema),
    tags=["users"]
)
