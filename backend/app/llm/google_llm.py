"""
Cortex Engineering — Google Gemini LLM Service.

Integrates with Google Generative AI (Gemini 2.0 Flash / Gemini 1.5 Flash).
"""

from __future__ import annotations

import asyncio
from typing import Optional

from app.core.exceptions import InternalServerError
from app.core.logging import get_logger
from app.llm.base import BaseLLMService

logger = get_logger("google_llm")


class GoogleLLMService(BaseLLMService):
    """Google Gemini generation service."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._configured = False

    def _ensure_configured(self):
        if not self._configured:
            import google.generativeai as genai

            genai.configure(api_key=self._api_key)
            self._configured = True

    def _sync_generate(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        import google.generativeai as genai

        self._ensure_configured()
        model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            ),
        )
        response = model.generate_content(user_prompt)
        return response.text

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> str:
        try:
            return await asyncio.to_thread(
                self._sync_generate, system_prompt, user_prompt, temperature
            )
        except Exception as exc:
            logger.error("Gemini API generation failed", error=str(exc))
            raise InternalServerError(f"Google Gemini generation error: {exc}") from exc
