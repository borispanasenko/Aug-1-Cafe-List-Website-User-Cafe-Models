from fastapi import Depends
from app.app_configs import Configs
from fastapi_users import BaseUserManager, UUIDIDMixin
from app.app_core.domain.models.user_model import UserModel
from app.app_core.core_dependencies.user_dependencies import get_user_db
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from typing import Optional
from fastapi import Request
from uuid import UUID


SECRET_KEY = Configs.SECRET_KEY


#  UserManager используется в роутах fastapi_users посредством get_user_manager()
class UserManager(UUIDIDMixin, BaseUserManager[UserModel, UUID]):
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(self, user: UserModel, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserModel, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserModel, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
