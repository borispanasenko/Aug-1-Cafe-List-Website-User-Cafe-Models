from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import AsyncSessionLocal


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as db:
        yield db


"""


📌 Разделим по слоям:
🔧 SessionLocal
— это инфраструктурная штука,
— создаётся в database.py,
— обёртка над engine, фабрика сессий.
📍 Она ничего не знает о FastAPI, Depends, или жизненном цикле запроса.

🧩 get_db()
— это уже зависимость (dependency),
— она использует инфраструктуру (SessionLocal) и адаптирует её под FastAPI,
— возвращает Session на время запроса,
— и делает это в виде генератора, чтобы можно было использовать 
yield-зависимости с автоматическим закрытием.


"""