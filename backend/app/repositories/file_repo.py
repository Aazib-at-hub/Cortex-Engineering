"""
Cortex Engineering — File Data Access.

Database operations for RepositoryFile entity.
"""

from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import RepositoryFile


class FileRepository:
    """Data access operations for RepositoryFile."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, file_entity: RepositoryFile) -> RepositoryFile:
        """Persist new file record."""
        self._session.add(file_entity)
        await self._session.flush()
        await self._session.refresh(file_entity)
        return file_entity

    async def create_batch(self, files: list[RepositoryFile]) -> list[RepositoryFile]:
        """Persist batch of file records."""
        self._session.add_all(files)
        await self._session.flush()
        for f in files:
            await self._session.refresh(f)
        return files

    async def get_by_id(self, file_id: UUID) -> Optional[RepositoryFile]:
        """Fetch file by ID."""
        result = await self._session.execute(
            select(RepositoryFile).where(RepositoryFile.id == file_id)
        )
        return result.scalar_one_or_none()

    async def get_by_repo_and_path(
        self, repository_id: UUID, path: str
    ) -> Optional[RepositoryFile]:
        """Fetch file by repository ID and relative path."""
        result = await self._session.execute(
            select(RepositoryFile).where(
                RepositoryFile.repository_id == repository_id,
                RepositoryFile.path == path,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_repository(
        self, repository_id: UUID
    ) -> Sequence[RepositoryFile]:
        """Fetch all files belonging to repository."""
        result = await self._session.execute(
            select(RepositoryFile)
            .where(RepositoryFile.repository_id == repository_id)
            .order_by(RepositoryFile.path.asc())
        )
        return result.scalars().all()
