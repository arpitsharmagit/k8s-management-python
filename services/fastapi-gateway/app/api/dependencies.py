"""API — FastAPI dependency injection.

Provides:
  - get_current_user(): validates JWT bearer token → User domain object
  - require_role(): factory for role-based access guards
  - get_device_service(): injects DeviceService with DB session
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.auth_service import auth_service
from app.application.device_service import DeviceService
from app.domain.models.user import Role, User
from app.infrastructure.db.database import AsyncSession, get_session
from app.infrastructure.db.repos.device_repo_impl import SQLDeviceRepository
from app.infrastructure.db.repos.user_repo_impl import SQLUserRepository

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Validate JWT and return the authenticated User domain entity."""
    payload = auth_service.decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = auth_service.extract_user_id(payload)
    user_repo = SQLUserRepository(session)
    user = await user_repo.find_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def require_role(minimum: Role):
    """Dependency factory — raises 403 if the user's role is insufficient."""
    async def _check(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if not current_user.has_role(minimum):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {minimum.value} or higher",
            )
        return current_user
    return _check


async def get_device_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DeviceService:
    """Inject DeviceService wired with the current DB session."""
    repo = SQLDeviceRepository(session)
    return DeviceService(repo)
