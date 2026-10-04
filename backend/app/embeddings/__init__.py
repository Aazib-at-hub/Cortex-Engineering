"""
Cortex Engineering — Embedding Service Factory.
"""

from functools import lru_cache

from app.core.config import get_settings
from app.embeddings.base import BaseEmbeddingService
from app.embeddings.local_embeddings import LocalEmbeddingService
from app.embeddings.openai_embeddings import OpenAIEmbeddingService

__all__ = ["BaseEmbeddingService", "LocalEmbeddingService", "OpenAIEmbeddingService", "get_embedding_service"]


@lru_cache
def get_embedding_service() -> BaseEmbeddingService:
    """Return configured embedding service singleton."""
    settings = get_settings()
    if settings.embedding_provider.lower() == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY required when EMBEDDING_PROVIDER=openai")
        return OpenAIEmbeddingService(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    return LocalEmbeddingService(
        model_name=settings.embedding_model,
        dimension=settings.embedding_dimension,
    )
