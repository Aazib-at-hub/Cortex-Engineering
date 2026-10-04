"""
Cortex Engineering — Chat API Routes.

Endpoints for asking questions via RAG, listing conversations,
viewing message histories with source citations, and deleting conversations.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.database.session import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse,
    SourceResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(tags=["Chat"])


@router.post(
    "/repositories/{repo_id}/chat",
    response_model=ChatResponse,
    summary="Ask a question about a repository (RAG)",
)
async def chat_with_repository(
    repo_id: UUID,
    data: ChatRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Ask a question against the indexed repository codebase."""
    service = ChatService(db)
    conv, assistant_msg, sources = await service.ask_question(
        user_id=current_user_id,
        repository_id=repo_id,
        question=data.question,
        conversation_id=data.conversation_id,
    )

    msg_resp = MessageResponse(
        id=assistant_msg.id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        sources=[SourceResponse.model_validate(s) for s in sources],
        created_at=assistant_msg.created_at,
    )

    return ChatResponse(
        conversation_id=conv.id,
        message=msg_resp,
    )


@router.get(
    "/repositories/{repo_id}/conversations",
    response_model=list[ConversationResponse],
    summary="List conversations for repository",
)
async def list_conversations(
    repo_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[ConversationResponse]:
    """Retrieve all conversations belonging to given repository."""
    service = ChatService(db)
    convs = await service.list_conversations(repo_id, current_user_id)
    return [
        ConversationResponse(
            id=c.id,
            repository_id=c.repository_id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=len(c.messages) if hasattr(c, "messages") and c.messages else 0,
        )
        for c in convs
    ]


@router.get(
    "/conversations/{conv_id}",
    response_model=ConversationDetailResponse,
    summary="Get conversation detail with messages",
)
async def get_conversation(
    conv_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ConversationDetailResponse:
    """Retrieve full message history and citations for conversation."""
    service = ChatService(db)
    conv = await service.get_conversation(conv_id, current_user_id)

    formatted_messages: list[MessageResponse] = []
    for m in conv.messages:
        formatted_messages.append(
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                sources=[SourceResponse.model_validate(s) for s in m.sources] if m.sources else [],
                created_at=m.created_at,
            )
        )

    return ConversationDetailResponse(
        id=conv.id,
        repository_id=conv.repository_id,
        title=conv.title,
        messages=formatted_messages,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.delete(
    "/conversations/{conv_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete conversation",
)
async def delete_conversation(
    conv_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete a conversation and its messages."""
    service = ChatService(db)
    await service.delete_conversation(conv_id, current_user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
