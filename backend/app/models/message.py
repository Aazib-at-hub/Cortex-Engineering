"""
Cortex Engineering — Message and MessageSource Models.

Message represents a single chat message (user or assistant).
MessageSource links an assistant message to the code chunks it cited,
preserving the answer → chunk → file → line provenance chain.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class Message(Base, UUIDMixin, TimestampMixin):
    """A single message in a conversation (user or assistant)."""

    __tablename__ = "messages"

    # Ownership
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Content
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sources = relationship(
        "MessageSource", back_populates="message", cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("ix_messages_conversation_id", "conversation_id"),
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} role={self.role}>"


class MessageSource(Base, UUIDMixin):
    """
    Links an assistant message to the code chunk it cited.

    Preserves the full provenance chain:
    Answer → MessageSource → CodeChunk → File → Repository
    """

    __tablename__ = "message_sources"

    # Relationships
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("code_chunks.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Denormalized source info for fast display without joining
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    similarity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    message = relationship("Message", back_populates="sources")
    chunk = relationship("CodeChunk", back_populates="message_sources")

    # Indexes
    __table_args__ = (
        Index("ix_message_sources_message_id", "message_id"),
    )

    def __repr__(self) -> str:
        return f"<MessageSource message={self.message_id} file={self.file_path}>"
