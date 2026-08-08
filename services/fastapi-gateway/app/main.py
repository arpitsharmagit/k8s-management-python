"""
FastAPI Gateway — Application Entry Point

Wires together all routers, middleware, lifespan events (DB init,
MQTT client startup), and OpenAPI metadata.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.infrastructure.db.database import init_db
from app.infrastructure.mqtt.mqtt_client import mqtt_client
from app.api.routers import auth, devices, telemetry

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup → yield → shutdown."""
    logger.info("Starting up FastAPI IoT Gateway...")
    await init_db()
    mqtt_client.connect()
    yield
    logger.info("Shutting down FastAPI IoT Gateway...")
    mqtt_client.disconnect()


app = FastAPI(
    title="IoT Admin Gateway",
    description=(
        "Enterprise FastAPI gateway for IoT device registration, "
        "telemetry ingestion, direct-method invocation, and JWT RBAC."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe endpoint."""
    return {"status": "ok", "service": "fastapi-gateway", "version": "1.0.0"}
