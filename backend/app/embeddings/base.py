"""
Cortex Engineering — Embedding Service Base Interface.

Defines the contract for embedding providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEmbeddingService(ABC):
    """Abstract interface for embedding text chunks and queries."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector dimensionality of embeddings."""
        ...

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of text strings in batch.

        Args:
            texts: List of text content strings.

        Returns:
            List of float vector lists, matched 1:1 with input texts.
        """
        ...

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a single search query string.

        Args:
            query: User search or question string.

        Returns:
            Single float vector list.
        """
        ...
