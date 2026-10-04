"""
Cortex Engineering — FastAPI Dependencies.

Shared dependency functions used across API routes for authentication,
database sessions, and authorization checks.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError
from app.core.security import decode_access_token
from app.database.session import get_db


async def get_current_user_id(
    authorization: str = Header(..., description="Bearer <token>"),
) -> UUID:
    """
    Extract and validate the current user ID from the Authorization header.

    Args:
        authorization: The Authorization header value (Bearer <token>).

    Returns:
        The authenticated user's UUID.

    Raises:
        InvalidTokenError: If the token is missing, malformed, or expired.
    """
    if not authorization.startswith("Bearer "):
        raise InvalidTokenError("Authorization header must start with 'Bearer '")

    token = authorization[7:]  # Strip "Bearer " prefix
    if not token:
        raise InvalidTokenError("Token is empty")

    return decode_access_token(token)
