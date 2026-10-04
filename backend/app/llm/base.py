"""
Cortex Engineering — LLM Service Base Interface.

Defines the contract for LLM generation backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMService(ABC):
    """Abstract interface for LLM text generation."""

    @abstractmethod
    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """
        Generate completion from system prompt and user question.

        Args:
            system_prompt: Guiding system instructions and untrusted data warnings.
            user_prompt: Context chunks and user question.
            temperature: LLM sampling temperature.

        Returns:
            Assistant response text.
        """
        ...
