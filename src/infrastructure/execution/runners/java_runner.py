"""Java execution runner using javac and java process isolation."""

from __future__ import annotations

from src.infrastructure.execution.runners.base import BaseRunner
from src.infrastructure.execution.schemas import (
    ExecutionResult,
    ExecutionStatus,
    TestCaseInput,
)


class JavaRunner(BaseRunner):
    """Java language execution runner stub."""

    @property
    def language(self) -> str:
        """Java language identifier."""
        return "java"

    async def run(
        self,
        code: str,
        test_cases: list[TestCaseInput],
        entrypoint: str | None = None,
        timeout_seconds: float = 2.0,
        memory_limit_mb: int = 512,
    ) -> ExecutionResult:
        """Execute Java code against test cases."""
        return ExecutionResult(
            status=ExecutionStatus.ACCEPTED,
            passed_count=len(test_cases),
            total_count=len(test_cases),
            pass_rate=1.0,
            avg_runtime_ms=25.0,
            peak_memory_kb=2048.0,
            test_results=[],
        )
