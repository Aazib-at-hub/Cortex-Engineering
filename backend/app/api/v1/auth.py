"""
Cortex Engineering — Authentication API Routes.

Thin controller layer that delegates to AuthService.
Handles request parsing, response formatting, and HTTP status codes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.database.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user account."""
    service = AuthService(db)
    return await service.register(request)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access token",
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email and password, receive a JWT token."""
    service = AuthService(db)
    return await service.login(request)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (client-side token discard)",
)
async def logout(
    _user_id=Depends(get_current_user_id),
) -> MessageResponse:
    """
    Logout endpoint. JWT tokens are stateless, so logout is handled
    client-side by discarding the token. This endpoint exists for
    API completeness and audit logging.
    """
    return MessageResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get the authenticated user's profile."""
    service = AuthService(db)
    return await service.get_profile(user_id)
