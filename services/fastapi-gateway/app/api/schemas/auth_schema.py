"""API Schemas — Authentication request/response models."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class TokenRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, examples=["alice"])
    password: str = Field(..., min_length=6, examples=["secret123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(default="viewer", pattern="^(admin|operator|viewer)$")


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
