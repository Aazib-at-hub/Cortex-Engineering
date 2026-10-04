"""
Cortex Engineering — Repository Data Access.

Database operations for the Repository entity. Enforces user ownership
on every query to prevent cross-user data access.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repository import Repository


class RepositoryRepository:
    """Data access layer for Repository entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, repo_id: UUID, user_id: UUID) -> Optional[Repository]:
        """Get a repository by ID, scoped to the owning user."""
        result = await self.db.execute(
            select(Repository).where(
                Repository.id == repo_id,
                Repository.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_unscoped(self, repo_id: UUID) -> Optional[Repository]:
        """
        Get a repository by ID without ownership scoping.

        INTERNAL USE ONLY — for background ingestion jobs that run without
        a request user. Never call from API-facing code paths.
        """
        result = await self.db.execute(select(Repository).where(Repository.id == repo_id))
        return result.scalar_one_or_none()

    async def get_by_url(self, github_url: str, user_id: UUID) -> Optional[Repository]:
        """Check if a user already imported this repository URL."""
        result = await self.db.execute(
            select(Repository).where(
                Repository.github_url == github_url,
                Repository.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[Repository]:
        """List all repositories owned by a user, ordered by creation date."""
        result = await self.db.execute(
            select(Repository)
            .where(Repository.user_id == user_id)
            .order_by(Repository.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, repository: Repository) -> Repository:
        """Persist a new repository."""
        self.db.add(repository)
        await self.db.flush()
        await self.db.refresh(repository)
        return repository

    async def update_status(
        self,
        repo_id: UUID,
        status: str,
        error_message: Optional[str] = None,
        file_count: Optional[int] = None,
        chunk_count: Optional[int] = None,
        languages: Optional[dict] = None,
        last_indexed_at: Optional[datetime] = None,
    ) -> None:
        """Update repository processing status and statistics."""
        values: dict = {"status": status}
        if status != "FAILED":
            values["error_message"] = None  # Clear stale errors on retry
        if last_indexed_at is not None:
            values["last_indexed_at"] = last_indexed_at
        if error_message is not None:
            values["error_message"] = error_message
        if file_count is not None:
            values["file_count"] = file_count
        if chunk_count is not None:
            values["chunk_count"] = chunk_count
        if languages is not None:
            values["languages"] = languages

        await self.db.execute(
            update(Repository).where(Repository.id == repo_id).values(**values)
        )
        await self.db.flush()

    async def delete(self, repo_id: UUID, user_id: UUID) -> bool:
        """Delete a repository and all associated data (cascading). Returns True if deleted."""
        result = await self.db.execute(
            delete(Repository).where(
                Repository.id == repo_id,
                Repository.user_id == user_id,
            )
        )
        await self.db.flush()
        return result.rowcount > 0


# Backwards compatibility alias
RepositoryRepo = RepositoryRepository

