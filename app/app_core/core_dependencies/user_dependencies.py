from fastapi import Depends
from collections.abc import AsyncGenerator

from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_dependencies.dependencies import get_db
from app.app_core.domain.models.user_model import UserModel


async def get_user_db(db: AsyncSession = Depends(get_db)) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    user_db = SQLAlchemyUserDatabase(db, UserModel)
    yield user_db
