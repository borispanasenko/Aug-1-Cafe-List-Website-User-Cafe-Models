from dataclasses import dataclass
from typing import Callable, Optional, Awaitable, Type
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


# Определим точные типы для читаемости
CreateFunc = Callable[[AsyncSession, BaseModel], Awaitable[Optional[object]]]
GetExistingFunc = Callable[[AsyncSession, BaseModel], Awaitable[Optional[object]]]
UpdateFunc = Callable[[AsyncSession, object, BaseModel], Awaitable[bool]]


async def _default_get_existing(_: AsyncSession, __: BaseModel) -> Optional[object]:
    return None


async def _default_update(_: AsyncSession, __: object, ___: BaseModel) -> bool:
    return False  # ничего не обновлено


@dataclass
class SeederConfig:
    name: str
    data: list[dict]
    schema: Type[BaseModel]
    create_func: CreateFunc  # обязателен
    get_existing_func: Optional[GetExistingFunc] = None
    update_func: Optional[UpdateFunc] = None

    async def seed_magic_run(self, db: AsyncSession):
        from runner import run_seed

        if not self.data:
            print(f"[SKIP] {self.name}: no data provided.")
            return

        if self.create_func is None:
            raise ValueError(f"{self.name}: create_func is required")

        print(f"[SEED] {self.name}")
        await run_seed(
            db=db,
            raw_data=self.data,
            schema=self.schema,
            create_func=self.create_func,
            get_existing_func=self.get_existing_func or _default_get_existing,
            update_func=self.update_func or _default_update,
        )