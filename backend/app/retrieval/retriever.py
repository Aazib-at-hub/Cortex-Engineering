"""
Cortex Engineering — Vector Retrieval Service.

Performs semantic search against pgvector embeddings scoped strictly to a repository,
returning top-K relevant code chunks with similarity scores and source file paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.logging import get_logger
from app.embeddings.base import BaseEmbeddingService
from app.models.chunk import CodeChunk
from app.models.file import RepositoryFile

logger = get_logger("retriever")


@dataclass(frozen=True)
class RetrievedChunk:
    """Retrieved chunk along with similarity score and file path information."""

    chunk_id: UUID
    file_id: UUID
    file_path: str
    file_name: str
    language: str
    content: str
    start_line: int
    end_line: int
    similarity_score: float


class RetrieverService:
    """Executes semantic search over repository code chunks."""

    def __init__(
        self,
        session: AsyncSession,
        embedding_service: BaseEmbeddingService,
    ) -> None:
        self._session = session
        self._embedding_service = embedding_service

    async def retrieve(
        self,
        repository_id: UUID,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
    ) -> list[RetrievedChunk]:
        """
        Embed search query and retrieve closest chunks in pgvector.

        Args:
            repository_id: Scoping repository UUID.
            query: User's question or search term.
            top_k: Maximum number of chunks to return.
            similarity_threshold: Minimum cosine similarity score (0.0 - 1.0).

        Returns:
            List of RetrievedChunk instances sorted descending by similarity.
        """
        # 1. Embed query
        query_vector = await self._embedding_service.embed_query(query)

        # 2. Query pgvector cosine distance
        cosine_dist = CodeChunk.embedding.cosine_distance(query_vector)
        stmt = (
            select(CodeChunk, cosine_dist.label("distance"))
            .options(joinedload(CodeChunk.file))
            .where(CodeChunk.repository_id == repository_id)
            .where(CodeChunk.embedding.is_not(None))
            .order_by(cosine_dist.asc())
            .limit(top_k * 2)  # Fetch extra to filter by threshold
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        retrieved: list[RetrievedChunk] = []
        for chunk, dist in rows:
            # Cosine similarity = 1.0 - distance
            score = max(0.0, 1.0 - float(dist)) if dist is not None else 0.0
            if score < similarity_threshold:
                continue

            file_obj: RepositoryFile = chunk.file
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    file_id=chunk.file_id,
                    file_path=file_obj.path if file_obj else "unknown",
                    file_name=file_obj.filename if file_obj else "unknown",
                    language=chunk.language or "plaintext",
                    content=chunk.content,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    similarity_score=round(score, 4),
                )
            )
            if len(retrieved) >= top_k:
                break

        logger.info(
            "Retrieved chunks for query",
            repo_id=str(repository_id),
            count=len(retrieved),
            top_score=retrieved[0].similarity_score if retrieved else 0.0,
        )
        return retrieved
