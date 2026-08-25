"""Асинхронное подключение к БД."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def create_worker_engine():
    """Движок для Celery: без пула, только текущий asyncio.run."""
    return create_async_engine(settings.database_url, poolclass=NullPool)
