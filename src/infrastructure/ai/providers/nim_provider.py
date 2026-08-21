"""NVIDIA NIM LLM Provider wrapper."""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI
from loguru import logger

from src.core.config.settings import settings
from src.infrastructure.ai.providers.base import BaseLLMProvider
from src.infrastructure.ai.schemas import LLMMessage, LLMResponse


class NimLLMProvider(BaseLLMProvider):
    """NVIDIA NIM LLM provider integration."""

    @property
    def name(self) -> str:
        """Provider name."""
        return "nim"

    @property
    def supported_models(self) -> list[str]:
        """Supported NVIDIA NIM model names."""
        return ["nvidia/nemotron-3-super-120b-a12b", "meta/llama-3.3-70b-instruct"]

    def _get_client(self) -> AsyncOpenAI | None:
        """Get an initialized AsyncOpenAI client configured for NIM."""
        if not settings.nim_api_key:
            return None
        return AsyncOpenAI(
            base_url=settings.nim_base_url,
            api_key=settings.nim_api_key,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Generate response via NIM API."""
        start_time = time.perf_counter()
        selected_model = model or "nvidia/nemotron-3-super-120b-a12b"
        client = self._get_client()

        if not client:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return LLMResponse(
                content="NIM Gateway (Fallback): API Key not configured.",
                model_name=selected_model,
                provider_name=self.name,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_ms=round(elapsed_ms, 2),
                finish_reason="stop",
            )

        try:
            formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
            response = await client.chat.completions.create(
                model=selected_model,
                messages=formatted_messages, # type: ignore
                temperature=temperature,
                max_tokens=max_tokens or 1024,
                top_p=0.9,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            content = response.choices[0].message.content or ""

            return LLMResponse(
                content=content,
                model_name=selected_model,
                provider_name=self.name,
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0,
                latency_ms=round(elapsed_ms, 2),
                finish_reason=response.choices[0].finish_reason or "stop",
            )
        except Exception as e:
            logger.error(f"NIM generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens via NIM API."""
        selected_model = model or "nvidia/nemotron-3-super-120b-a12b"
        client = self._get_client()

        if not client:
            yield "NIM Gateway (Fallback): API Key not configured."
            return

        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        try:
            stream = await client.chat.completions.create(
                model=selected_model,
                messages=formatted_messages, # type: ignore
                temperature=temperature,
                max_tokens=max_tokens or 1024,
                top_p=0.9,
                stream=True,
            )

            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content is not None:
                    yield delta.content
                    
        except Exception as e:
            logger.error(f"NIM stream error: {e}")
            raise

