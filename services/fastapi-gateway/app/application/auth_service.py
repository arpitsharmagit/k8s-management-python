"""Application Service — Authentication.

Handles JWT token creation/verification and password hashing.
Depends only on domain models and stdlib — no FastAPI imports.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.domain.models.user import Role, User

logger = logging.getLogger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Stateless authentication/authorisation service."""

    def hash_password(self, plain: str) -> str:
        return _pwd_context.hash(plain)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)

    def create_access_token(self, user: User) -> str:
        """Issue a signed HS256 JWT containing user id, username, and role."""
        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": expire,
        }
        return jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode and validate a JWT. Returns the payload dict or None."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError as exc:
            logger.warning("JWT decode failed: %s", exc)
            return None

    def extract_role(self, payload: dict) -> Role:
        return Role(payload.get("role", Role.VIEWER.value))

    def extract_user_id(self, payload: dict) -> str:
        return payload.get("sub", "")


auth_service = AuthService()
