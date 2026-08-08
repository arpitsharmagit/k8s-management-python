"""Domain model — User entity and Role enum."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    """RBAC roles in ascending privilege order."""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"

    def can_write(self) -> bool:
        return self in (Role.OPERATOR, Role.ADMIN)

    def is_admin(self) -> bool:
        return self == Role.ADMIN


@dataclass
class User:
    """Core domain entity — an authenticated API user."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    hashed_password: str = ""
    role: Role = Role.VIEWER
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def has_role(self, required: Role) -> bool:
        """Check if this user has at least the required role level."""
        order = [Role.VIEWER, Role.OPERATOR, Role.ADMIN]
        return order.index(self.role) >= order.index(required)
