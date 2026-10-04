"""
Cortex Engineering — Simple Decision Service (MVP Default).

Pass-through decision service that preserves vector-similarity ordering.
Can be swapped with JEV (Judged Evaluation & Validation) when enabled.
"""

from __future__ import annotations

from typing import Sequence

from app.decision.base import BaseDecisionService
from app.retrieval.retriever import RetrievedChunk


class SimpleDecisionService(BaseDecisionService):
    """Transparent passthrough decision service."""

    async def filter_and_rank(
        self,
        query: str,
        chunks: Sequence[RetrievedChunk],
    ) -> Sequence[RetrievedChunk]:
        # Transparent pass-through for MVP baseline
        return chunks
