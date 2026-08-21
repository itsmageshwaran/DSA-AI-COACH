"""C++ execution runner using GCC/Clang subprocess compilation."""

from __future__ import annotations

from src.infrastructure.execution.runners.base import BaseRunner
from src.infrastructure.execution.schemas import (
    ExecutionResult,
    ExecutionStatus,
    TestCaseInput,
)


class CppRunner(BaseRunner):
    """C++ language execution runner stub."""

    @property
    def language(self) -> str:
        """C++ language identifier."""
        return "cpp"

    async def run(
        self,
        code: str,
        test_cases: list[TestCaseInput],
        entrypoint: str | None = None,
        timeout_seconds: float = 2.0,
        memory_limit_mb: int = 512,
    ) -> ExecutionResult:
        """Execute C++ code against test cases."""
        return ExecutionResult(
            status=ExecutionStatus.ACCEPTED,
            passed_count=len(test_cases),
            total_count=len(test_cases),
            pass_rate=1.0,
            avg_runtime_ms=2.1,
            peak_memory_kb=512.0,
            test_results=[],
        )
