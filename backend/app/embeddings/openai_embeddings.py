"""
Cortex Engineering — OpenAI Embedding Service.

Generates embeddings using OpenAI API (e.g., text-embedding-3-small).
"""

from __future__ import annotations

from typing import Optional

from app.core.exceptions import InternalServerError
from app.core.logging import get_logger
from app.embeddings.base import BaseEmbeddingService

logger = get_logger("openai_embeddings")


class OpenAIEmbeddingService(BaseEmbeddingService):
    """OpenAI embedding generator."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "text-embedding-3-small",
        dimension: int = 1536,
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._dimension = dimension
        self._client: Optional[object] = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=self._api_key)
        return self._client

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        client = self._get_client()
        try:
            response = await client.embeddings.create(
                input=texts,
                model=self._model_name,
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error("OpenAI embedding API call failed", error=str(e))
            raise InternalServerError(f"Failed to generate embeddings: {e}") from e

    async def embed_query(self, query: str) -> list[float]:
        results = await self.embed_texts([query])
        return results[0]
