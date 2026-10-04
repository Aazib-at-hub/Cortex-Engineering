"""
Cortex Engineering — Code Chunk Model.

Represents a chunk of code/text extracted from a repository file,
along with its embedding vector for semantic similarity search.
The repository_id is denormalized to enable efficient repository-scoped
vector searches without joining through the files table.
"""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.database.base import Base, TimestampMixin, UUIDMixin


class CodeChunk(Base, UUIDMixin, TimestampMixin):
    """A semantic chunk of code or text with its embedding vector."""

    __tablename__ = "code_chunks"

    # Ownership (denormalized for query performance)
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Chunk metadata
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="text")

    # Embedding vector — dimension set via config
    # Note: The Vector dimension must match EMBEDDING_DIMENSION in config.
    # Default 384 for all-MiniLM-L6-v2. Change if using a different model.
    embedding = mapped_column(Vector(384), nullable=True)

    # Relationships
    file = relationship("RepositoryFile", back_populates="chunks")
    repository = relationship("Repository", back_populates="chunks")
    message_sources = relationship(
        "MessageSource", back_populates="chunk", lazy="noload"
    )

    # Indexes
    __table_args__ = (
        Index("ix_code_chunks_repository_id", "repository_id"),
        Index("ix_code_chunks_file_id", "file_id"),
    )

    def __repr__(self) -> str:
        return f"<CodeChunk id={self.id} file_id={self.file_id} index={self.chunk_index}>"
