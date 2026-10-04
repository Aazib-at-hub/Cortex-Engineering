"""
Cortex Engineering — User Model.

Represents registered users of the platform. Each user owns repositories,
conversations, and their associated data.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User account entity."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    # Relationships
    repositories = relationship(
        "Repository", back_populates="user", cascade="all, delete-orphan", lazy="noload"
    )
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"
