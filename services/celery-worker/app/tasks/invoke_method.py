"""Celery Task — invoke_method.

Relays a direct-method command to a device over MQTT.
This task is dispatched by the FastAPI gateway when an operator
calls POST /devices/{id}/invoke.
"""
from __future__ import annotations

import json
import logging

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

from app.celery_app import celery_app
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.invoke_method.invoke_method",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def invoke_method(self, device_id: str, method_name: str, payload: dict) -> dict:
    """Publish a direct-method command to the device via MQTT.

    Args:
        device_id: Target device UUID.
        method_name: Method to invoke (e.g. 'reboot', 'set_interval').
        payload: Method arguments as a dict.

    Returns:
        Result dict with publish status.
    """
    try:
        topic = f"devices/{device_id}/methods/{method_name}"
        message = json.dumps({
            "method": method_name,
            "device_id": device_id,
            "payload": payload,
        })

        publish.single(
            topic=topic,
            payload=message,
            hostname=settings.MQTT_HOST,
            port=settings.MQTT_PORT,
            qos=1,
            client_id=f"{settings.MQTT_CLIENT_ID}-pub",
        )

        logger.info(
            "Direct method dispatched | device=%s | method=%s | topic=%s",
            device_id, method_name, topic,
        )
        return {"device_id": device_id, "method": method_name, "topic": topic, "status": "published"}

    except Exception as exc:
        logger.error("MQTT invoke_method failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)
