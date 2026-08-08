"""API Schemas — Telemetry request/response models."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TelemetryIngestRequest(BaseModel):
    device_id: str = Field(..., examples=["550e8400-e29b-41d4-a716-446655440000"])
    payload: dict[str, Any] = Field(
        ...,
        examples=[{"temperature": 23.5, "humidity": 60.2, "battery_level": 87.0}],
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        description="Measurement timestamp (UTC). Defaults to server receipt time.",
    )


class TelemetryResponse(BaseModel):
    id: str
    device_id: str
    payload: dict[str, Any]
    timestamp: datetime
    received_at: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    battery_level: Optional[float] = None


class TelemetryIngestResponse(BaseModel):
    id: str
    device_id: str
    status: str = "accepted"
    queued: bool = True
