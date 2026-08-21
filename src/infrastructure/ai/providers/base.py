"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from src.infrastructure.ai.schemas import LLMMessage, LLMResponse


class BaseLLMProvider(ABC):
    """Abstract base LLM provider."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier name (e.g., 'openai', 'anthropic', 'mock')."""

    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        """List of supported model identifiers."""

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Generate complete LLM response asynchronously."""

    @abstractmethod
    def generate_stream(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response tokens asynchronously."""
