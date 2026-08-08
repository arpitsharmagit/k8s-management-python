"""Infrastructure — Concrete DeviceRepository implementation (SQLAlchemy)."""
from __future__ import annotations

import json
import logging
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.device import Device, DeviceStatus
from app.domain.repositories.device_repo import AbstractDeviceRepository
from app.infrastructure.db.models import DeviceORM

logger = logging.getLogger(__name__)


def _orm_to_domain(row: DeviceORM) -> Device:
    return Device(
        id=row.id,
        name=row.name,
        device_type=row.device_type,
        location=row.location or "",
        status=DeviceStatus(row.status),
        firmware_version=row.firmware_version or "",
        mqtt_topic=row.mqtt_topic or "",
        owner_id=row.owner_id or "",
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _domain_to_orm(device: Device) -> DeviceORM:
    return DeviceORM(
        id=device.id,
        name=device.name,
        device_type=device.device_type,
        location=device.location,
        status=device.status.value,
        firmware_version=device.firmware_version,
        mqtt_topic=device.mqtt_topic,
        owner_id=device.owner_id or None,
        created_at=device.created_at,
        updated_at=device.updated_at,
    )


class SQLDeviceRepository(AbstractDeviceRepository):
    """SQLAlchemy-backed implementation of AbstractDeviceRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, device: Device) -> Device:
        existing = await self._session.get(DeviceORM, device.id)
        if existing:
            existing.name = device.name
            existing.device_type = device.device_type
            existing.location = device.location
            existing.status = device.status.value
            existing.firmware_version = device.firmware_version
            existing.mqtt_topic = device.mqtt_topic
            existing.updated_at = device.updated_at
        else:
            self._session.add(_domain_to_orm(device))
        await self._session.flush()
        return device

    async def find_by_id(self, device_id: str) -> Optional[Device]:
        row = await self._session.get(DeviceORM, device_id)
        return _orm_to_domain(row) if row else None

    async def find_all(self, skip: int = 0, limit: int = 100) -> list[Device]:
        result = await self._session.execute(
            select(DeviceORM).offset(skip).limit(limit)
        )
        return [_orm_to_domain(r) for r in result.scalars().all()]

    async def delete(self, device_id: str) -> bool:
        result = await self._session.execute(
            delete(DeviceORM).where(DeviceORM.id == device_id)
        )
        return result.rowcount > 0

    async def find_by_owner(self, owner_id: str) -> list[Device]:
        result = await self._session.execute(
            select(DeviceORM).where(DeviceORM.owner_id == owner_id)
        )
        return [_orm_to_domain(r) for r in result.scalars().all()]
