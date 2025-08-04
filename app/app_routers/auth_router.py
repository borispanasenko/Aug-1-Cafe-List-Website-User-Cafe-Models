# –––––––––––––––––– USER AUTH IMPORTS –––––––––––––––––– #

from fastapi import APIRouter
from app.infrastructure.auth_backend import auth_backend, fastapi_users
from app.app_core.domain.schemas.user_schemas import UserCreateSchema, UserReadSchema


# ––––––––––––––––––––––––– ROUTER ––––––––––––––––––––––––– #

router = APIRouter(prefix='/auth', tags=['auth'])

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserReadSchema, UserCreateSchema),
    tags=["auth"]
)
