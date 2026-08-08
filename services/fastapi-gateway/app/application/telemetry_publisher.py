"""Application Service — Telemetry event publisher.

After telemetry is ingested via the API, this service publishes
a Celery task to the Redis broker so event workers can process it.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime

from celery import Celery

from app.config import settings
from app.domain.models.telemetry import Telemetry

logger = logging.getLogger(__name__)

# Lightweight Celery producer — only used to publish tasks, not consume them.
_celery_producer = Celery(
    "fastapi_producer",
    broker=settings.CELERY_BROKER_URL,
)


class TelemetryPublisher:
    """Publishes telemetry events to the Celery/Redis broker."""

    def publish_telemetry_event(self, telemetry: Telemetry) -> None:
        """Send a `process_telemetry` task to the Celery broker."""
        event = {
            "id": telemetry.id,
            "device_id": telemetry.device_id,
            "payload": telemetry.payload,
            "timestamp": telemetry.timestamp.isoformat(),
            "received_at": telemetry.received_at.isoformat(),
        }
        _celery_producer.send_task(
            "app.tasks.process_telemetry.process_telemetry",
            args=[event],
            queue="telemetry",
        )
        logger.debug("Published telemetry event for device %s", telemetry.device_id)

    def publish_device_status_event(self, device_id: str, status: str) -> None:
        """Send a `sync_device_status` task to the Celery broker."""
        _celery_producer.send_task(
            "app.tasks.sync_device_status.sync_device_status",
            args=[device_id, status],
            queue="device_status",
        )
        logger.debug("Published status event: device=%s status=%s", device_id, status)


telemetry_publisher = TelemetryPublisher()
