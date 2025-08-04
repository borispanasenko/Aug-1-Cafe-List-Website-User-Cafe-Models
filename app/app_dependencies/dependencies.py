from app.infrastructure.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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