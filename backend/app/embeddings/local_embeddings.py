"""
Cortex Engineering — Local Sentence-Transformers Embedding Service.

Runs embedding inference locally using sentence-transformers (default: all-MiniLM-L6-v2).
Executes synchronous model calls inside asyncio.to_thread to maintain an unblocked event loop.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from app.core.logging import get_logger
from app.embeddings.base import BaseEmbeddingService

logger = get_logger("local_embeddings")


class LocalEmbeddingService(BaseEmbeddingService):
    """Local embedding generator using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384) -> None:
        self._model_name = model_name
        self._dimension = dimension
        self._model: Optional[object] = None

    def _load_model(self):
        """Lazy load model on first usage."""
        if self._model is None:
            logger.info("Loading local embedding model", model=self._model_name)
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    def _sync_embed(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [arr.tolist() for arr in embeddings]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await asyncio.to_thread(self._sync_embed, texts)

    async def embed_query(self, query: str) -> list[float]:
        results = await self.embed_texts([query])
        return results[0]
