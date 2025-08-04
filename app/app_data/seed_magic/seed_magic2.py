from typing import List, Type, TypeVar

from app.app_data.categories_data import categories_data

from app.app_data.cafes_data import cafes_data
from app.app_core.domain.schemas.cafe_schemas import CafeCreateSchema
from app.app_core.domain.services.cafe_service import create_cafe

from pydantic import BaseModel, ValidationError
from app.app_dependencies.dependencies import get_db
from sqlalchemy.orm import Session
import sys


Schema = TypeVar('Schema', bound=BaseModel)


def validate(raw_data: List[dict], schema: Type[Schema]) -> List[Schema]:
    validated = []
    for i, entity in enumerate(raw_data):
        try:
            validated.append(schema(**entity))
        except ValidationError as e:
            print(f'Validation error at number {i}: {e}')
    return validated


def run_seed(db: Session, raw_data: List[dict], schema: Type[Schema], create_func):
    validated = validate(raw_data, schema)
    for entity in validated:
        create_func(db, entity)


if __name__ == "__main__":
    try:
        db = next(get_db())
        run_seed(db, cafes_data, CafeCreateSchema, create_cafe)
        print('Success seeding cafes')
        run_seed(db, categories_data, CafeCreateSchema, create_cafe)
        print('Success seeding cafes')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
