"""Unified AI Gateway and LLM Model Router."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import ClassVar

from src.infrastructure.ai.providers.base import BaseLLMProvider
from src.infrastructure.ai.providers.mock_provider import MockLLMProvider
from src.infrastructure.ai.providers.openai_provider import OpenAILLMProvider
from src.infrastructure.ai.providers.nim_provider import NimLLMProvider
from src.infrastructure.ai.schemas import LLMMessage, LLMResponse, TaskType


class AIGateway:
    """Unified AI Gateway orchestrating model routing, provider failover, and telemetry."""

    _providers: ClassVar[dict[str, BaseLLMProvider]] = {
        "mock": MockLLMProvider(),
        "openai": OpenAILLMProvider(),
        "nim": NimLLMProvider(),
    }

    _task_model_map: ClassVar[dict[TaskType, tuple[str, str]]] = {
        TaskType.SOCRATIC_TUTOR: ("nim", "nvidia/nemotron-3-super-120b-a12b"),
        TaskType.CODE_REVIEW: ("nim", "nvidia/nemotron-3-super-120b-a12b"),
        TaskType.COMPLEXITY_ANALYSIS: ("nim", "meta/llama-3.3-70b-instruct"),
        TaskType.HINT_GENERATION: ("nim", "meta/llama-3.3-70b-instruct"),
        TaskType.GENERAL_QA: ("nim", "meta/llama-3.3-70b-instruct"),
    }

    def __init__(self, default_provider: str = "mock") -> None:
        self.default_provider_name = default_provider

    def register_provider(self, provider: BaseLLMProvider) -> None:
        """Register a custom LLM provider strategy."""
        self._providers[provider.name.lower()] = provider

    def resolve_provider_and_model(
        self,
        task_type: TaskType | None = None,
        provider_override: str | None = None,
        model_override: str | None = None,
    ) -> tuple[BaseLLMProvider, str]:
        """Resolve target provider instance and model identifier based on task type or overrides."""
        target_provider_name = provider_override or self.default_provider_name
        target_model = model_override

        if task_type and not provider_override and not model_override:
            task_provider_name, task_model = self._task_model_map.get(
                task_type, (self.default_provider_name, "mock-gpt-4o")
            )
            # If default provider is mock, keep mock provider name
            if self.default_provider_name == "mock":
                target_provider_name = "mock"
                target_model = f"mock-{task_model}"
            else:
                target_provider_name = task_provider_name
                target_model = task_model

        provider = self._providers.get(target_provider_name.lower())
        if not provider:
            provider = self._providers["mock"]

        final_model = target_model or provider.supported_models[0]
        return provider, final_model

    async def generate(
        self,
        messages: list[LLMMessage],
        task_type: TaskType | None = None,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Dispatch generation request through resolved provider strategy."""
        resolved_provider, resolved_model = self.resolve_provider_and_model(
            task_type=task_type,
            provider_override=provider,
            model_override=model,
        )

        try:
            return await resolved_provider.generate(
                messages=messages,
                model=resolved_model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception:
            # Fallback to Mock provider on provider failure
            fallback_provider = self._providers["mock"]
            return await fallback_provider.generate(
                messages=messages,
                model="mock-fallback",
                temperature=temperature,
                max_tokens=max_tokens,
            )

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        task_type: TaskType | None = None,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncGenerator[str, None]:
        """Stream generation response tokens through resolved provider strategy."""
        resolved_provider, resolved_model = self.resolve_provider_and_model(
            task_type=task_type,
            provider_override=provider,
            model_override=model,
        )

        async for chunk in resolved_provider.generate_stream(
            messages=messages,
            model=resolved_model,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk


ai_gateway = AIGateway(default_provider="nim")

