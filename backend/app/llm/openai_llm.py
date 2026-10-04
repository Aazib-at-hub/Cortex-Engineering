"""
Cortex Engineering — OpenAI LLM Service.

Integrates with OpenAI chat completions API (e.g. gpt-4o-mini).
"""

from __future__ import annotations

from typing import Optional

from app.core.exceptions import InternalServerError
from app.core.logging import get_logger
from app.llm.base import BaseLLMService

logger = get_logger("openai_llm")


class OpenAILLMService(BaseLLMService):
    """OpenAI generation service."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini") -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._client: Optional[object] = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=self._api_key)
        return self._client

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> str:
        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=self._model_name,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("OpenAI chat completion failed", error=str(exc))
            raise InternalServerError(f"OpenAI generation error: {exc}") from exc
