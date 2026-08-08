"""Domain model — Device entity."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    PROVISIONING = "provisioning"
    ERROR = "error"


@dataclass
class Device:
    """Core domain entity — represents a registered IoT device."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    device_type: str = ""
    location: str = ""
    status: DeviceStatus = DeviceStatus.PROVISIONING
    firmware_version: str = ""
    mqtt_topic: str = ""
    owner_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_online(self) -> None:
        self.status = DeviceStatus.ONLINE
        self.updated_at = datetime.utcnow()

    def mark_offline(self) -> None:
        self.status = DeviceStatus.OFFLINE
        self.updated_at = datetime.utcnow()

    @property
    def default_mqtt_topic(self) -> str:
        return f"devices/{self.id}/telemetry"
