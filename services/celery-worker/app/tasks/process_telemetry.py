"""Celery Task — process_telemetry.

Receives a telemetry event dict published by the FastAPI gateway,
logs it, and can be extended to write to a time-series store, trigger
alerts, or forward to downstream analytics.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.process_telemetry.process_telemetry",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def process_telemetry(self, event: dict) -> dict:
    """Process a telemetry event received from the FastAPI gateway.

    Args:
        event: {
            "id": str,
            "device_id": str,
            "payload": dict,
            "timestamp": str (ISO 8601),
            "received_at": str (ISO 8601),
        }

    Returns:
        A processing result dict.
    """
    try:
        device_id = event.get("device_id", "unknown")
        payload = event.get("payload", {})
        ts = event.get("timestamp", datetime.utcnow().isoformat())

        logger.info(
            "Processing telemetry | device=%s | timestamp=%s | keys=%s",
            device_id, ts, list(payload.keys()),
        )

        # ── Extension point: persist to time-series DB, trigger alert, etc. ──
        temperature = payload.get("temperature")
        if temperature is not None and temperature > 80:
            logger.warning(
                "HIGH TEMPERATURE ALERT | device=%s | temp=%.1f°C", device_id, temperature
            )

        return {
            "status": "processed",
            "device_id": device_id,
            "event_id": event.get("id"),
        }

    except Exception as exc:
        logger.error("Telemetry processing failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)
