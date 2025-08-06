from dataclasses import dataclass
from typing import Callable, Optional, Awaitable, Type
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class SeederConfig:
    name: str
    data: list[dict]
    schema: Type[BaseModel]
    create_func: Callable[[AsyncSession, BaseModel], Awaitable[Optional[object]]] = None
    get_existing_func: Optional[Callable[[AsyncSession, BaseModel], Awaitable[Optional[object]]]] = None
    update_func: Optional[Callable[[AsyncSession, object, BaseModel], Awaitable[bool]]] = None

    async def seed_magic_run(self, db: AsyncSession):
        from runner import run_seed
        if not self.data:
            print(f"[SKIP] {self.name}: no data provided.")
            return
        print(f"[SEED] {self.name}")
        await run_seed(
            db=db,
            raw_data=self.data,
            schema=self.schema,
            get_existing_func=self.get_existing_func or None,
            create_func=self.create_func,
            update_func=self.update_func or None,
        )

