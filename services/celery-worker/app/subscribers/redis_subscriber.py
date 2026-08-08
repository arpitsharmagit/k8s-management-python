"""Redis Pub/Sub Subscriber — listens for device events and dispatches Celery tasks.

This process runs as a daemon alongside the Celery worker.
It subscribes to Redis channels and dispatches the appropriate
Celery task for each event type received.

Channels:
  - iot:telemetry     → dispatches process_telemetry task
  - iot:device:status → dispatches sync_device_status task
  - iot:methods       → dispatches invoke_method task
"""
from __future__ import annotations

import json
import logging
import signal
import sys
import time

import redis

from app.config import settings
from app.tasks.process_telemetry import process_telemetry
from app.tasks.sync_device_status import sync_device_status
from app.tasks.invoke_method import invoke_method

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

CHANNELS = ["iot:telemetry", "iot:device:status", "iot:methods"]
_running = True


def handle_shutdown(signum, frame):
    global _running
    logger.info("Shutdown signal received — stopping Redis subscriber...")
    _running = False


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def dispatch(channel: str, data: dict) -> None:
    """Dispatch the correct Celery task based on the pub/sub channel."""
    try:
        if channel == "iot:telemetry":
            process_telemetry.apply_async(args=[data], queue="telemetry")
            logger.debug("Dispatched process_telemetry for device %s", data.get("device_id"))

        elif channel == "iot:device:status":
            device_id = data.get("device_id")
            status = data.get("status", "offline")
            sync_device_status.apply_async(args=[device_id, status], queue="device_status")
            logger.debug("Dispatched sync_device_status for device %s → %s", device_id, status)

        elif channel == "iot:methods":
            invoke_method.apply_async(
                args=[data.get("device_id"), data.get("method"), data.get("payload", {})],
                queue="methods",
            )
            logger.debug("Dispatched invoke_method for device %s", data.get("device_id"))

        else:
            logger.warning("Unknown channel: %s", channel)

    except Exception as exc:
        logger.error("Failed to dispatch task from channel '%s': %s", channel, exc, exc_info=True)


def run() -> None:
    """Connect to Redis and listen on all IoT event channels."""
    logger.info("Starting Redis Pub/Sub subscriber on channels: %s", CHANNELS)

    while _running:
        try:
            client = redis.from_url(settings.REDIS_PUBSUB_URL, decode_responses=True)
            pubsub = client.pubsub()
            pubsub.subscribe(*CHANNELS)
            logger.info("Subscribed to Redis channels: %s", CHANNELS)

            for message in pubsub.listen():
                if not _running:
                    break
                if message["type"] != "message":
                    continue
                try:
                    data = json.loads(message["data"])
                    dispatch(channel=message["channel"], data=data)
                except json.JSONDecodeError as exc:
                    logger.warning("Malformed JSON on channel %s: %s", message["channel"], exc)

        except redis.exceptions.ConnectionError as exc:
            logger.error("Redis connection lost: %s — retrying in 5s...", exc)
            time.sleep(5)
        except Exception as exc:
            logger.error("Unexpected subscriber error: %s", exc, exc_info=True)
            time.sleep(5)

    logger.info("Redis subscriber stopped.")


if __name__ == "__main__":
    run()
