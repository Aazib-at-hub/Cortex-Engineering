"""
Cortex Engineering — Decision Service Base Interface.

Defines the contract for chunk filtering, reranking, and decision routing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from app.retrieval.retriever import RetrievedChunk


class BaseDecisionService(ABC):
    """Abstract interface for decision and reranking layers."""

    @abstractmethod
    async def filter_and_rank(
        self,
        query: str,
        chunks: Sequence[RetrievedChunk],
    ) -> Sequence[RetrievedChunk]:
        """
        Evaluate and rerank retrieved chunks before passing to generation.
        """
        ...
