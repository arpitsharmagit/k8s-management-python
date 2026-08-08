"""API Router — Authentication: /auth/token, /auth/register."""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth_schema import (
    RegisterRequest,
    TokenRequest,
    TokenResponse,
    UserResponse,
)
from app.api.dependencies import get_current_user, require_role
from app.application.auth_service import auth_service
from app.domain.models.user import Role, User
from app.infrastructure.db.database import get_session
from app.infrastructure.db.repos.user_repo_impl import SQLUserRepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Issue JWT access token",
    status_code=status.HTTP_200_OK,
)
async def login(
    body: TokenRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    """Authenticate with username + password and receive a signed HS256 JWT."""
    repo = SQLUserRepository(session)
    user = await repo.find_by_username(body.username)
    if not user or not auth_service.verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    token = auth_service.create_access_token(user)
    logger.info("User '%s' authenticated (role=%s)", user.username, user.role.value)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_minutes=60,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register a new user (admin only)",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def register_user(
    body: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    """Create a new user with a specified role. Requires admin JWT."""
    repo = SQLUserRepository(session)
    existing = await repo.find_by_username(body.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{body.username}' already exists",
        )
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=auth_service.hash_password(body.password),
        role=Role(body.role),
    )
    saved = await repo.save(user)
    return UserResponse(
        id=saved.id,
        username=saved.username,
        email=saved.email,
        role=saved.role.value,
        is_active=saved.is_active,
    )


@router.get("/me", response_model=UserResponse, summary="Get current user info")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
    )
