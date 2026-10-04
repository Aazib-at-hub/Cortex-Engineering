"""
Cortex Engineering — RAG Answer Generator.

Connects vector retrieval, prompt compilation, LLM inference, and source attribution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
from uuid import UUID

from app.core.logging import get_logger
from app.llm.base import BaseLLMService
from app.rag.prompt import SYSTEM_PROMPT, build_user_prompt
from app.retrieval.retriever import RetrievedChunk

logger = get_logger("rag_generator")


@dataclass(frozen=True)
class GeneratedCitation:
    """Citation metadata for chunks included in LLM context."""

    chunk_id: UUID
    file_path: str
    start_line: int
    end_line: int
    similarity_score: float


@dataclass(frozen=True)
class RAGResult:
    """Answer text bundled with cited sources."""

    answer: str
    citations: list[GeneratedCitation]


class RAGGenerator:
    """Orchestrates generation of grounded answers with source citations."""

    def __init__(self, llm_service: BaseLLMService) -> None:
        self._llm = llm_service

    async def generate_answer(
        self,
        question: str,
        retrieved_chunks: Sequence[RetrievedChunk],
        temperature: float = 0.2,
    ) -> RAGResult:
        """
        Build prompt from context chunks, generate response from LLM, and return with citations.
        """
        user_prompt = build_user_prompt(question, retrieved_chunks)

        logger.info(
            "Generating RAG answer",
            question_len=len(question),
            context_chunks=len(retrieved_chunks),
        )

        answer_text = await self._llm.generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=temperature,
        )

        citations = [
            GeneratedCitation(
                chunk_id=c.chunk_id,
                file_path=c.file_path,
                start_line=c.start_line,
                end_line=c.end_line,
                similarity_score=c.similarity_score,
            )
            for c in retrieved_chunks
        ]

        return RAGResult(answer=answer_text, citations=citations)
