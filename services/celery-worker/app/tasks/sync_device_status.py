"""Celery Task — sync_device_status.

Receives a device status change event and updates the device record
in the database.
"""
from __future__ import annotations

import logging

from sqlalchemy import create_engine, text

from app.celery_app import celery_app
from app.config import settings

logger = logging.getLogger(__name__)

# Sync SQLAlchemy engine for Celery tasks
_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)


@celery_app.task(
    name="app.tasks.sync_device_status.sync_device_status",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def sync_device_status(self, device_id: str, status: str) -> dict:
    """Update the status of a device in the database.

    Args:
        device_id: UUID of the device to update.
        status: New status string ('online' | 'offline' | 'error').

    Returns:
        A result dict with device_id and updated status.
    """
    try:
        logger.info("Syncing device status | device=%s | status=%s", device_id, status)

        with _engine.begin() as conn:
            result = conn.execute(
                text(
                    "UPDATE devices SET status = :status, updated_at = NOW() "
                    "WHERE id = :device_id"
                ),
                {"status": status, "device_id": device_id},
            )
            if result.rowcount == 0:
                logger.warning("Device %s not found in DB — status sync skipped", device_id)

        return {"device_id": device_id, "status": status, "synced": True}

    except Exception as exc:
        logger.error("Device status sync failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)
