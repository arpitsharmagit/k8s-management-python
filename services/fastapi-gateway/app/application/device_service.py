"""Application Service — Device management use cases."""
from __future__ import annotations

import logging
from typing import Optional

from app.domain.models.device import Device, DeviceStatus
from app.domain.repositories.device_repo import AbstractDeviceRepository
from app.infrastructure.mqtt.mqtt_client import mqtt_client

logger = logging.getLogger(__name__)


class DeviceService:
    """Use cases for IoT device lifecycle management."""

    def __init__(self, repo: AbstractDeviceRepository) -> None:
        self._repo = repo

    async def register_device(
        self,
        name: str,
        device_type: str,
        location: str,
        firmware_version: str,
        owner_id: str,
    ) -> Device:
        """Register a new IoT device and persist it."""
        device = Device(
            name=name,
            device_type=device_type,
            location=location,
            firmware_version=firmware_version,
            owner_id=owner_id,
        )
        device.mqtt_topic = device.default_mqtt_topic
        saved = await self._repo.save(device)
        logger.info("Registered device %s (id=%s)", name, saved.id)
        return saved

    async def get_device(self, device_id: str) -> Optional[Device]:
        return await self._repo.find_by_id(device_id)

    async def list_devices(self, skip: int = 0, limit: int = 100) -> list[Device]:
        return await self._repo.find_all(skip=skip, limit=limit)

    async def delete_device(self, device_id: str) -> bool:
        deleted = await self._repo.delete(device_id)
        if deleted:
            logger.info("Deleted device id=%s", device_id)
        return deleted

    async def invoke_direct_method(
        self,
        device_id: str,
        method_name: str,
        payload: dict,
    ) -> dict:
        """Send a direct-method command to a device via MQTT.

        Publishes to: devices/{device_id}/methods/{method_name}
        """
        device = await self._repo.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        topic = f"devices/{device_id}/methods/{method_name}"
        import json
        mqtt_client.publish(topic, json.dumps(payload))
        logger.info(
            "Invoked method '%s' on device %s via topic '%s'",
            method_name, device_id, topic,
        )
        return {"status": "dispatched", "topic": topic, "method": method_name}

    async def update_device_status(
        self, device_id: str, status: DeviceStatus
    ) -> Optional[Device]:
        device = await self._repo.find_by_id(device_id)
        if not device:
            return None
        device.status = status
        return await self._repo.save(device)
