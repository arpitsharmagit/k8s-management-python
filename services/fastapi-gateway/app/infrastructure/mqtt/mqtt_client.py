"""Infrastructure — paho-mqtt MQTT client wrapper.

Used by the FastAPI gateway to publish direct-method commands
and device provisioning messages to the Mosquitto broker.
"""
from __future__ import annotations

import json
import logging
import threading

import paho.mqtt.client as mqtt

from app.config import settings

logger = logging.getLogger(__name__)


class MQTTClient:
    """Thread-safe paho-mqtt wrapper for publishing messages."""

    def __init__(self) -> None:
        self._client = mqtt.Client(
            client_id=settings.MQTT_CLIENT_ID,
            clean_session=True,
            protocol=mqtt.MQTTv311,
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish
        self._lock = threading.Lock()
        self._connected = False

    def _on_connect(self, client, userdata, flags, rc, props=None) -> None:
        if rc == 0:
            self._connected = True
            logger.info("MQTT connected to %s:%s", settings.MQTT_HOST, settings.MQTT_PORT)
        else:
            logger.error("MQTT connection failed with code %s", rc)

    def _on_disconnect(self, client, userdata, rc, props=None) -> None:
        self._connected = False
        logger.warning("MQTT disconnected (rc=%s)", rc)

    def _on_publish(self, client, userdata, mid) -> None:
        logger.debug("MQTT message published (mid=%s)", mid)

    def connect(self) -> None:
        """Connect to the Mosquitto broker and start the network loop."""
        try:
            self._client.connect(
                host=settings.MQTT_HOST,
                port=settings.MQTT_PORT,
                keepalive=60,
            )
            self._client.loop_start()
        except Exception as exc:
            logger.error("Failed to connect to MQTT broker: %s", exc)

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
        logger.info("MQTT client disconnected.")

    def publish(self, topic: str, payload: str | dict, qos: int = 1) -> None:
        """Publish a message to the given MQTT topic."""
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        with self._lock:
            result = self._client.publish(topic, payload, qos=qos)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error("MQTT publish failed on topic '%s': rc=%s", topic, result.rc)


mqtt_client = MQTTClient()
