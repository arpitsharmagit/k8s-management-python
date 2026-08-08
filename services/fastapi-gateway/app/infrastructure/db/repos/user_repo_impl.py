"""Infrastructure — Concrete UserRepository implementation (SQLAlchemy)."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.user import Role, User
from app.domain.repositories.user_repo import AbstractUserRepository
from app.infrastructure.db.models import UserORM

logger = logging.getLogger(__name__)


def _orm_to_domain(row: UserORM) -> User:
    return User(
        id=row.id,
        username=row.username,
        email=row.email,
        hashed_password=row.hashed_password,
        role=Role(row.role),
        is_active=row.is_active,
        created_at=row.created_at,
    )


def _domain_to_orm(user: User) -> UserORM:
    return UserORM(
        id=user.id,
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
    )


class SQLUserRepository(AbstractUserRepository):
    """SQLAlchemy-backed implementation of AbstractUserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> User:
        existing = await self._session.get(UserORM, user.id)
        if existing:
            existing.username = user.username
            existing.email = user.email
            existing.hashed_password = user.hashed_password
            existing.role = user.role.value
            existing.is_active = user.is_active
        else:
            self._session.add(_domain_to_orm(user))
        await self._session.flush()
        return user

    async def find_by_id(self, user_id: str) -> Optional[User]:
        row = await self._session.get(UserORM, user_id)
        return _orm_to_domain(row) if row else None

    async def find_by_username(self, username: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserORM).where(UserORM.username == username)
        )
        row = result.scalar_one_or_none()
        return _orm_to_domain(row) if row else None

    async def find_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self._session.execute(
            select(UserORM).offset(skip).limit(limit)
        )
        return [_orm_to_domain(r) for r in result.scalars().all()]

    async def delete(self, user_id: str) -> bool:
        from sqlalchemy import delete
        result = await self._session.execute(
            delete(UserORM).where(UserORM.id == user_id)
        )
        return result.rowcount > 0
