"""API Schemas — Device request/response models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeviceRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Temperature Sensor 01"])
    device_type: str = Field(..., examples=["temperature-sensor"])
    location: str = Field(default="", examples=["Building A - Floor 2"])
    firmware_version: str = Field(default="1.0.0", examples=["2.3.1"])


class DeviceResponse(BaseModel):
    id: str
    name: str
    device_type: str
    location: str
    status: str
    firmware_version: str
    mqtt_topic: str
    owner_id: str
    created_at: datetime
    updated_at: datetime


class DirectMethodRequest(BaseModel):
    method_name: str = Field(..., examples=["reboot", "set_interval"])
    payload: dict = Field(default_factory=dict, examples=[{"interval_ms": 5000}])


class DirectMethodResponse(BaseModel):
    status: str
    topic: str
    method: str
