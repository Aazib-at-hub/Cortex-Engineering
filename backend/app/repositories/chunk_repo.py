"""
Cortex Engineering — Code Chunk Data Access.

Database operations for CodeChunk entity including vector retrieval queries.
"""

from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import CodeChunk


class ChunkRepository:
    """Data access operations for CodeChunk."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, chunk: CodeChunk) -> CodeChunk:
        """Persist new chunk."""
        self._session.add(chunk)
        await self._session.flush()
        await self._session.refresh(chunk)
        return chunk

    async def create_batch(self, chunks: list[CodeChunk]) -> list[CodeChunk]:
        """Persist batch of chunks."""
        self._session.add_all(chunks)
        await self._session.flush()
        return chunks

    async def get_by_id(self, chunk_id: UUID) -> Optional[CodeChunk]:
        """Fetch chunk by ID."""
        result = await self._session.execute(
            select(CodeChunk).where(CodeChunk.id == chunk_id)
        )
        return result.scalar_one_or_none()

    async def list_by_file(self, file_id: UUID) -> Sequence[CodeChunk]:
        """List chunks for a specific file ordered by index."""
        result = await self._session.execute(
            select(CodeChunk)
            .where(CodeChunk.file_id == file_id)
            .order_by(CodeChunk.chunk_index.asc())
        )
        return result.scalars().all()

    async def search_similar(
        self,
        repository_id: UUID,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[tuple[CodeChunk, float]]:
        """
        Search chunks using cosine distance in pgvector.

        Returns tuples of (chunk, similarity_score).
        Cosine similarity = 1 - cosine distance.
        """
        distance = CodeChunk.embedding.cosine_distance(query_embedding)
        query = (
            select(CodeChunk, distance.label("distance"))
            .where(CodeChunk.repository_id == repository_id)
            .where(CodeChunk.embedding.is_not(None))
            .order_by(distance.asc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        rows = result.all()
        return [(chunk, max(0.0, 1.0 - float(dist))) for chunk, dist in rows]
