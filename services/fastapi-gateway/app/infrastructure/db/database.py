"""Infrastructure — SQLAlchemy async database engine and session factory."""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.APP_ENV == "development"),
    future=True,
    # PostgreSQL pool settings (ignored by SQLite)
    pool_pre_ping=True,
)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""
    pass


async def init_db() -> None:
    """Create all tables (dev/test convenience). Production uses Alembic."""
    async with engine.begin() as conn:
        from app.infrastructure.db import models  # noqa: F401 — registers models
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialised.")


async def get_session() -> AsyncSession:  # type: ignore[return]
    """FastAPI dependency — yields an async DB session per request."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
