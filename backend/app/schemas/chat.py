"""
Cortex Engineering — Chat Schemas.

Request and response schemas for chat messages, conversations,
and source citations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Requests ─────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    """Chat question request."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural-language question about the repository",
    )
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID to continue. If null, creates a new conversation.",
    )


# ── Responses ────────────────────────────────────────────────────────────────


class SourceResponse(BaseModel):
    """A source citation linking an answer to repository code."""

    file_path: str
    start_line: int
    end_line: int
    similarity_score: Optional[float] = None
    chunk_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """A single chat message with optional source citations."""

    id: UUID
    role: str
    content: str
    sources: list[SourceResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Response to a chat question, including the conversation context."""

    conversation_id: UUID
    message: MessageResponse


class ConversationResponse(BaseModel):
    """Conversation summary for listing."""

    id: UUID
    repository_id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    """Full conversation with all messages."""

    id: UUID
    repository_id: UUID
    title: Optional[str] = None
    messages: list[MessageResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
