"""
Cortex Engineering — Message Data Access.

Database operations for Message and MessageSource entities.
"""

from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message, MessageSource


class MessageRepository:
    """Data access operations for Message and MessageSource."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_message(self, message: Message) -> Message:
        """Persist message record."""
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        return message

    async def create_source(self, source: MessageSource) -> MessageSource:
        """Persist message citation source."""
        self._session.add(source)
        await self._session.flush()
        return source

    async def create_sources_batch(
        self, sources: list[MessageSource]
    ) -> list[MessageSource]:
        """Persist batch of message citation sources."""
        self._session.add_all(sources)
        await self._session.flush()
        return sources

    async def list_by_conversation(
        self, conversation_id: UUID
    ) -> Sequence[Message]:
        """List messages for conversation ordered chronologically."""
        result = await self._session.execute(
            select(Message)
            .options(selectinload(Message.sources))
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()
