"""Domain model — Telemetry entity."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Telemetry:
    """Core domain entity — a single telemetry reading from a device."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    received_at: datetime = field(default_factory=datetime.utcnow)

    # Optional enrichment fields
    temperature: float | None = None
    humidity: float | None = None
    pressure: float | None = None
    battery_level: float | None = None

    def enrich_from_payload(self) -> None:
        """Extract well-known fields from the raw payload dict."""
        self.temperature = self.payload.get("temperature")
        self.humidity = self.payload.get("humidity")
        self.pressure = self.payload.get("pressure")
        self.battery_level = self.payload.get("battery_level")
