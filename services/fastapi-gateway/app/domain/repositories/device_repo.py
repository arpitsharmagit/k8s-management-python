"""Abstract repository interface — Device."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.device import Device


class AbstractDeviceRepository(ABC):
    """Port (interface) for device persistence.

    The infrastructure layer provides concrete implementations.
    The application layer depends only on this abstract class.
    """

    @abstractmethod
    async def save(self, device: Device) -> Device:
        """Persist a new or updated device. Returns the saved entity."""
        ...

    @abstractmethod
    async def find_by_id(self, device_id: str) -> Optional[Device]:
        """Return a device by its UUID, or None if not found."""
        ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> list[Device]:
        """Return a paginated list of all devices."""
        ...

    @abstractmethod
    async def delete(self, device_id: str) -> bool:
        """Delete a device by UUID. Returns True if deleted, False if not found."""
        ...

    @abstractmethod
    async def find_by_owner(self, owner_id: str) -> list[Device]:
        """Return all devices belonging to the given user."""
        ...
