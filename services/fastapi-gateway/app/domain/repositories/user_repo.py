"""Abstract repository interface — User."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.user import User


class AbstractUserRepository(ABC):
    """Port (interface) for user persistence."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Persist a new or updated user. Returns the saved entity."""
        ...

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Return a user by UUID, or None if not found."""
        ...

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        """Return a user by username, or None if not found."""
        ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Return a paginated list of all users."""
        ...

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete a user by UUID. Returns True if deleted."""
        ...
