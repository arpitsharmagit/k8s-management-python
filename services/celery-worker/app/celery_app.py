"""Celery Application — instance and configuration."""
from __future__ import annotations

import logging

from celery import Celery

from app.config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

celery_app = Celery(
    "iot_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.process_telemetry",
        "app.tasks.sync_device_status",
        "app.tasks.invoke_method",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.process_telemetry.*": {"queue": "telemetry"},
        "app.tasks.sync_device_status.*": {"queue": "device_status"},
        "app.tasks.invoke_method.*": {"queue": "methods"},
    },
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
