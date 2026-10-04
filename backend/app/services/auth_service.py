"""
Cortex Engineering — Authentication Service.

Handles user registration, login, and profile retrieval.
Business logic lives here; the API layer is a thin controller.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
)
from app.core.logging import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

logger = get_logger(__name__)


class AuthService:
    """Authentication and user management business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, request: RegisterRequest) -> UserResponse:
        """
        Register a new user.

        Raises:
            UserAlreadyExistsError: If email or username is already taken.
        """
        # Check for existing email
        existing = await self.user_repo.get_by_email(request.email)
        if existing:
            raise UserAlreadyExistsError("email")

        # Check for existing username
        existing = await self.user_repo.get_by_username(request.username)
        if existing:
            raise UserAlreadyExistsError("username")

        # Create user with hashed password
        user = User(
            email=request.email,
            username=request.username,
            password_hash=hash_password(request.password),
        )
        user = await self.user_repo.create(user)

        logger.info("user_registered", user_id=str(user.id), username=user.username)
        return UserResponse.model_validate(user)

    async def login(self, request: LoginRequest) -> TokenResponse:
        """
        Authenticate a user and return a JWT token.

        Raises:
            AuthenticationError: If credentials are invalid.
        """
        user = await self.user_repo.get_by_email(request.email)
        if not user:
            raise AuthenticationError()

        if not verify_password(request.password, user.password_hash):
            raise AuthenticationError()

        token = create_access_token(user.id)

        logger.info("user_login", user_id=str(user.id))
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    async def get_profile(self, user_id: UUID) -> UserResponse:
        """
        Get the current user's profile.

        Raises:
            AuthenticationError: If the user doesn't exist (token references deleted user).
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        return UserResponse.model_validate(user)
