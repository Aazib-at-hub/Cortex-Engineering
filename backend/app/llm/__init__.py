"""
Cortex Engineering — LLM Service Factory.
"""

from functools import lru_cache

from app.core.config import get_settings
from app.llm.base import BaseLLMService
from app.llm.google_llm import GoogleLLMService
from app.llm.openai_llm import OpenAILLMService

__all__ = ["BaseLLMService", "GoogleLLMService", "OpenAILLMService", "get_llm_service"]


@lru_cache
def get_llm_service() -> BaseLLMService:
    """Return configured LLM service singleton."""
    settings = get_settings()
    if settings.llm_provider.lower() == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY required when LLM_PROVIDER=openai")
        return OpenAILLMService(
            api_key=settings.openai_api_key,
            model_name=settings.llm_model,
        )
    # Default to Google Gemini
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY required when LLM_PROVIDER=google")
    return GoogleLLMService(
        api_key=settings.google_api_key,
        model_name=settings.llm_model,
    )
