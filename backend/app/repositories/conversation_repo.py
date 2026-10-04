"""
Cortex Engineering — Conversation Data Access.

Database operations for Conversation entity scoped by user ownership.
"""

from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation


class ConversationRepository:
    """Data access operations for Conversation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, conversation: Conversation) -> Conversation:
        """Persist new conversation."""
        self._session.add(conversation)
        await self._session.flush()
        await self._session.refresh(conversation)
        return conversation

    async def get_by_id(
        self, conversation_id: UUID, user_id: UUID
    ) -> Optional[Conversation]:
        """Fetch conversation by ID scoped to owner with messages and sources preloaded."""
        result = await self._session.execute(
            select(Conversation)
            .options(
                selectinload(Conversation.messages),
            )
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_repository(
        self, repository_id: UUID, user_id: UUID
    ) -> Sequence[Conversation]:
        """List all conversations for repository owned by user."""
        result = await self._session.execute(
            select(Conversation)
            .where(
                Conversation.repository_id == repository_id,
                Conversation.user_id == user_id,
            )
            .order_by(Conversation.updated_at.desc())
        )
        return result.scalars().all()

    async def delete(self, conversation_id: UUID, user_id: UUID) -> bool:
        """Delete conversation owned by user."""
        conv = await self.get_by_id(conversation_id, user_id)
        if not conv:
            return False
        await self._session.delete(conv)
        await self._session.flush()
        return True
