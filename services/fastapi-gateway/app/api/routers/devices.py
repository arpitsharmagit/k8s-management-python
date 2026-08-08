"""API Router — IoT Devices: CRUD + direct-method invocation."""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import get_current_user, get_device_service, require_role
from app.api.schemas.device_schema import (
    DeviceRegisterRequest,
    DeviceResponse,
    DirectMethodRequest,
    DirectMethodResponse,
)
from app.application.device_service import DeviceService
from app.domain.models.user import Role, User

logger = logging.getLogger(__name__)
router = APIRouter()


def _to_response(device) -> DeviceResponse:
    return DeviceResponse(
        id=device.id,
        name=device.name,
        device_type=device.device_type,
        location=device.location,
        status=device.status.value,
        firmware_version=device.firmware_version,
        mqtt_topic=device.mqtt_topic,
        owner_id=device.owner_id,
        created_at=device.created_at,
        updated_at=device.updated_at,
    )


@router.post(
    "/register",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new IoT device",
    dependencies=[Depends(require_role(Role.OPERATOR))],
)
async def register_device(
    body: DeviceRegisterRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    svc: Annotated[DeviceService, Depends(get_device_service)],
) -> DeviceResponse:
    """Register a new IoT device. Requires operator or admin role."""
    device = await svc.register_device(
        name=body.name,
        device_type=body.device_type,
        location=body.location,
        firmware_version=body.firmware_version,
        owner_id=current_user.id,
    )
    return _to_response(device)


@router.get(
    "/",
    response_model=list[DeviceResponse],
    summary="List all registered devices",
    dependencies=[Depends(require_role(Role.VIEWER))],
)
async def list_devices(
    skip: int = 0,
    limit: int = 100,
    svc: Annotated[DeviceService, Depends(get_device_service)] = None,
) -> list[DeviceResponse]:
    devices = await svc.list_devices(skip=skip, limit=limit)
    return [_to_response(d) for d in devices]


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Get device by ID",
    dependencies=[Depends(require_role(Role.VIEWER))],
)
async def get_device(
    device_id: str,
    svc: Annotated[DeviceService, Depends(get_device_service)] = None,
) -> DeviceResponse:
    device = await svc.get_device(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return _to_response(device)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    summary="Delete a device (admin only)",
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_device(
    device_id: str,
    svc: Annotated[DeviceService, Depends(get_device_service)] = None,
) -> None:
    deleted = await svc.delete_device(device_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")


@router.post(
    "/{device_id}/invoke",
    response_model=DirectMethodResponse,
    summary="Invoke a direct method on a device via MQTT",
    dependencies=[Depends(require_role(Role.OPERATOR))],
)
async def invoke_method(
    device_id: str,
    body: DirectMethodRequest,
    svc: Annotated[DeviceService, Depends(get_device_service)] = None,
) -> DirectMethodResponse:
    """Send a direct-method command to the device over MQTT."""
    try:
        result = await svc.invoke_direct_method(
            device_id=device_id,
            method_name=body.method_name,
            payload=body.payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return DirectMethodResponse(**result)
