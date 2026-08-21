"""Mock LLM provider for offline testing and deterministic evaluation."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator

from src.infrastructure.ai.providers.base import BaseLLMProvider
from src.infrastructure.ai.schemas import LLMMessage, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for deterministic testing."""

    @property
    def name(self) -> str:
        """Provider name."""
        return "mock"

    @property
    def supported_models(self) -> list[str]:
        """Supported mock model names."""
        return ["mock-gpt-4o", "mock-claude-3-5-sonnet", "mock-local-deepseek"]

    async def generate(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Generate deterministic mock LLM response."""
        start_time = time.perf_counter()
        selected_model = model or self.supported_models[0]
        user_prompt = next((m.content for m in reversed(messages) if m.role == "user"), "")

        # Formulate intelligent mock response
        if "socratic" in user_prompt.lower() or "hint" in user_prompt.lower():
            reply = (
                "What is the time complexity of your inner loop? "
                "Consider what happens when the array contains duplicate elements."
            )
        elif "complexity" in user_prompt.lower():
            reply = "The current solution operates in O(N^2) time complexity and O(1) auxiliary space complexity."
        elif "review" in user_prompt.lower():
            reply = "Code structure looks clean. Recommendation: add input bounds check for empty list scenarios."
        else:
            reply = f"Mock AI Coach response to: '{user_prompt[:50]}...'"

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        prompt_tokens = sum(len(m.content.split()) for m in messages)
        completion_tokens = len(reply.split())

        return LLMResponse(
            content=reply,
            model_name=selected_model,
            provider_name=self.name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=round(elapsed_ms, 2),
            finish_reason="stop",
        )

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncGenerator[str, None]:
        """Stream mock response tokens with small artificial delays."""
        res = await self.generate(messages, model, temperature, max_tokens)
        words = res.content.split(" ")
        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)
