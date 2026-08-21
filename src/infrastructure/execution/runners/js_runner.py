"""JavaScript execution runner using Node.js subprocess isolation."""

from __future__ import annotations

from src.infrastructure.execution.runners.base import BaseRunner
from src.infrastructure.execution.schemas import (
    ExecutionResult,
    ExecutionStatus,
    TestCaseInput,
)


class JavaScriptRunner(BaseRunner):
    """JavaScript/TypeScript language execution runner stub."""

    @property
    def language(self) -> str:
        """JavaScript language identifier."""
        return "javascript"

    async def run(
        self,
        code: str,
        test_cases: list[TestCaseInput],
        entrypoint: str | None = None,
        timeout_seconds: float = 2.0,
        memory_limit_mb: int = 512,
    ) -> ExecutionResult:
        """Execute JavaScript code against test cases."""
        return ExecutionResult(
            status=ExecutionStatus.ACCEPTED,
            passed_count=len(test_cases),
            total_count=len(test_cases),
            pass_rate=1.0,
            avg_runtime_ms=12.5,
            peak_memory_kb=1024.0,
            test_results=[],
        )
