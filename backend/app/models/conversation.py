"""
Cortex Engineering — Conversation Model.

Represents a chat conversation scoped to a specific repository.
A conversation belongs to a user and a repository, ensuring
data isolation between users and repos.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class Conversation(Base, UUIDMixin, TimestampMixin):
    """A chat conversation about a specific repository."""

    __tablename__ = "conversations"

    # Ownership
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Metadata
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    repository = relationship("Repository", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.created_at", lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("ix_conversations_user_repo", "user_id", "repository_id"),
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} repo={self.repository_id}>"
