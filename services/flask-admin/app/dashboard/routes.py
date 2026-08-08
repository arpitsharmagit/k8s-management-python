"""Flask Admin — Dashboard blueprint."""
from __future__ import annotations

import logging

import requests
from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required

from app.config import settings

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/")


def _api_get(path: str) -> tuple[list | dict, int]:
    """Helper: make an authenticated GET request to the FastAPI gateway."""
    try:
        resp = requests.get(
            f"{settings.FASTAPI_BASE_URL}{path}",
            headers={"Authorization": f"Bearer {current_user.token}"},
            timeout=5,
        )
        return resp.json(), resp.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot reach API gateway"}, 503
    except Exception as exc:
        logger.error("API call failed: %s", exc)
        return {"error": str(exc)}, 500


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    """Overview dashboard — summary cards + recent telemetry chart."""
    devices, status = _api_get("/devices/?limit=100")
    total_devices = len(devices) if isinstance(devices, list) else 0
    online = sum(1 for d in (devices if isinstance(devices, list) else []) if d.get("status") == "online")
    offline = total_devices - online

    return render_template(
        "dashboard/index.html",
        total_devices=total_devices,
        online=online,
        offline=offline,
        recent_devices=(devices[:5] if isinstance(devices, list) else []),
    )


@dashboard_bp.route("/devices")
@login_required
def devices():
    """Device list page."""
    page = int(request.args.get("page", 1))
    limit = 20
    skip = (page - 1) * limit
    data, _ = _api_get(f"/devices/?skip={skip}&limit={limit}")
    device_list = data if isinstance(data, list) else []
    return render_template("dashboard/devices.html", devices=device_list, page=page)


@dashboard_bp.route("/telemetry")
@login_required
def telemetry():
    """Telemetry view for a selected device."""
    device_id = request.args.get("device_id", "")
    telemetry_data = []
    if device_id:
        data, _ = _api_get(f"/telemetry/{device_id}?limit=30")
        telemetry_data = data if isinstance(data, list) else []
    devices, _ = _api_get("/devices/?limit=200")
    device_list = devices if isinstance(devices, list) else []
    return render_template(
        "dashboard/telemetry.html",
        devices=device_list,
        selected_device_id=device_id,
        telemetry=telemetry_data,
    )
