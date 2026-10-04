"""
Cortex Engineering — User Data Access.

Database operations for the User entity. All queries are parameterized
through SQLAlchemy ORM — no raw SQL.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Data access layer for User entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by their UUID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Persist a new user."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
