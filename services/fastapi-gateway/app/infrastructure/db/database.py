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

    # Create a default admin user for local/dev environments if it does not exist.
    from app.application.auth_service import auth_service
    from app.domain.models.user import Role, User
    from app.infrastructure.db.repos.user_repo_impl import SQLUserRepository

    async with AsyncSessionFactory() as session:
        repo = SQLUserRepository(session)
        existing = await repo.find_by_username(settings.ADMIN_USERNAME)
        if not existing:
            admin_user = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=auth_service.hash_password(settings.ADMIN_PASSWORD),
                role=Role.ADMIN,
                is_active=True,
            )
            await repo.save(admin_user)
            await session.commit()
            logger.info("Bootstrap admin user created: %s", settings.ADMIN_USERNAME)

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
