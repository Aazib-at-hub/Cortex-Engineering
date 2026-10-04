"""
Cortex Engineering — File Model.

Represents a discovered and filtered file within an imported repository.
Tracks file path, language, size, and content hash for deduplication.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class RepositoryFile(Base, UUIDMixin, TimestampMixin):
    """A single file within an imported repository."""

    __tablename__ = "files"

    # Ownership
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )

    # File metadata
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="text")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Relationships
    repository = relationship("Repository", back_populates="files")
    chunks = relationship(
        "CodeChunk", back_populates="file", cascade="all, delete-orphan", lazy="noload"
    )

    # Indexes
    __table_args__ = (
        Index("ix_files_repository_id", "repository_id"),
    )

    def __repr__(self) -> str:
        return f"<File id={self.id} path={self.path}>"


# Backwards compatibility alias
File = RepositoryFile

