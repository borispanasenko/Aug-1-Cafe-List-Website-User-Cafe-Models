import os
import asyncio
from sqlalchemy import pool
from dotenv import load_dotenv
from app.infrastructure.database import Base
from sqlalchemy.ext.asyncio import create_async_engine
from logging.config import fileConfig
from alembic import context
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()
DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'sqlite+aiosqlite:///./test.db')
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option('sqlalchemy.url', DATABASE_URL)

import app.app_core.domain.models   # noqa: F401
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    url = config.get_main_option('sqlalchemy.url')
    connectable_engine = create_async_engine(
        url=url,
        poolclass=pool.NullPool,
    )

    async with connectable_engine.begin() as connection:
        logger.info("Running Alembic migrations...")
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata,
                compare_type=True
            )
        )
        await connection.run_sync(lambda _: context.run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
