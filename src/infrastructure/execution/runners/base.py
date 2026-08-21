"""Abstract base runner interface for language execution engines."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.infrastructure.execution.schemas import ExecutionResult, TestCaseInput


class BaseRunner(ABC):
    """Abstract base runner for code execution engines."""

    @property
    @abstractmethod
    def language(self) -> str:
        """Supported programming language identifier (e.g., 'python', 'javascript', 'cpp')."""

    @abstractmethod
    async def run(
        self,
        code: str,
        test_cases: list[TestCaseInput],
        entrypoint: str | None = None,
        timeout_seconds: float = 2.0,
        memory_limit_mb: int = 512,
    ) -> ExecutionResult:
        """Run code against provided test cases under resource limits."""
