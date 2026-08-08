"""API Router — Telemetry: ingest + history retrieval."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session, require_role
from app.api.schemas.telemetry_schema import (
    TelemetryIngestRequest,
    TelemetryIngestResponse,
    TelemetryResponse,
)
from app.application.telemetry_publisher import telemetry_publisher
from app.domain.models.device import DeviceStatus
from app.domain.models.telemetry import Telemetry
from app.domain.models.user import Role
from app.infrastructure.db.models import DeviceORM, TelemetryORM
from app.infrastructure.db.repos.device_repo_impl import SQLDeviceRepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/ingest",
    response_model=TelemetryIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest telemetry from a device",
    dependencies=[Depends(require_role(Role.OPERATOR))],
)
async def ingest_telemetry(
    body: TelemetryIngestRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TelemetryIngestResponse:
    """Accept a telemetry payload, persist metadata, and publish a Celery event."""
    # Verify device exists
    device_repo = SQLDeviceRepository(session)
    device = await device_repo.find_by_id(body.device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    ts = body.timestamp or datetime.utcnow()
    telemetry = Telemetry(
        device_id=body.device_id,
        payload=body.payload,
        timestamp=ts,
    )
    telemetry.enrich_from_payload()

    # Persist ORM record
    orm_record = TelemetryORM(
        id=telemetry.id,
        device_id=telemetry.device_id,
        payload=json.dumps(telemetry.payload),
        timestamp=telemetry.timestamp,
        received_at=telemetry.received_at,
        temperature=telemetry.temperature,
        humidity=telemetry.humidity,
        pressure=telemetry.pressure,
        battery_level=telemetry.battery_level,
    )
    session.add(orm_record)

    # Mark device online
    device.mark_online()
    await device_repo.save(device)

    # Publish async Celery event (non-blocking)
    try:
        telemetry_publisher.publish_telemetry_event(telemetry)
    except Exception as exc:
        logger.warning("Could not publish Celery event: %s", exc)

    return TelemetryIngestResponse(id=telemetry.id, device_id=telemetry.device_id)


@router.get(
    "/{device_id}",
    response_model=list[TelemetryResponse],
    summary="Get telemetry history for a device",
    dependencies=[Depends(require_role(Role.VIEWER))],
)
async def get_telemetry(
    device_id: str,
    skip: int = 0,
    limit: int = 50,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> list[TelemetryResponse]:
    result = await session.execute(
        select(TelemetryORM)
        .where(TelemetryORM.device_id == device_id)
        .order_by(TelemetryORM.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        TelemetryResponse(
            id=r.id,
            device_id=r.device_id,
            payload=json.loads(r.payload),
            timestamp=r.timestamp,
            received_at=r.received_at,
            temperature=r.temperature,
            humidity=r.humidity,
            pressure=r.pressure,
            battery_level=r.battery_level,
        )
        for r in rows
    ]
