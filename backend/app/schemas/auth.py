"""
Cortex Engineering — Authentication Schemas.

Request and response schemas for user registration, login, and profile.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Requests ─────────────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    username: str = Field(
        ..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$"
    )
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


# ── Responses ────────────────────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Public user profile response."""

    id: UUID
    email: str
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
