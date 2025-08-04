from fastapi import Depends
from typing import Generator

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session

from app.app_dependencies.dependencies import get_db
from app.app_core.domain.models.user_model import UserModel


def get_user_db(db: Session = Depends(get_db)) -> Generator[SQLAlchemyUserDatabase, None, None]:
    user_db = SQLAlchemyUserDatabase(db, UserModel)
    yield user_db
