"""
Cortex Engineering — Security Utilities.

Handles password hashing (bcrypt) and JWT token creation/verification.
All secrets come from environment configuration — nothing is hard-coded.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import InvalidTokenError

# Password hashing context — bcrypt with automatic salt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: UUID,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        user_id: The user's UUID to encode in the token subject.
        expires_delta: Custom expiration time. Defaults to config value.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_expiration_minutes)

    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UUID:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT string.

    Returns:
        The user UUID from the token subject.

    Raises:
        InvalidTokenError: If the token is invalid, expired, or malformed.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            raise InvalidTokenError("Token missing subject claim")
        return UUID(user_id_str)
    except JWTError as exc:
        raise InvalidTokenError(f"Token validation failed: {exc}") from exc
    except ValueError as exc:
        raise InvalidTokenError(f"Invalid user ID in token: {exc}") from exc
