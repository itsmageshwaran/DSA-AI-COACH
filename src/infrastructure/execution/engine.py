"""Execution Engine manager dispatching code execution across language runners."""

from __future__ import annotations

from typing import ClassVar

from src.infrastructure.execution.runners.base import BaseRunner
from src.infrastructure.execution.runners.cpp_runner import CppRunner
from src.infrastructure.execution.runners.go_runner import GoRunner
from src.infrastructure.execution.runners.java_runner import JavaRunner
from src.infrastructure.execution.runners.js_runner import JavaScriptRunner
from src.infrastructure.execution.runners.python_runner import PythonRunner
from src.infrastructure.execution.schemas import ExecutionResult, TestCaseInput


class ExecutionEngine:
    """Multi-language code execution engine."""

    _runners: ClassVar[dict[str, BaseRunner]] = {
        "python": PythonRunner(),
        "javascript": JavaScriptRunner(),
        "js": JavaScriptRunner(),
        "cpp": CppRunner(),
        "c++": CppRunner(),
        "java": JavaRunner(),
        "go": GoRunner(),
    }

    @classmethod
    def register_runner(cls, runner: BaseRunner) -> None:
        """Register a custom language runner strategy."""
        cls._runners[runner.language.lower()] = runner

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """Return list of supported programming languages."""
        return sorted(cls._runners.keys())

    async def run_code(
        self,
        code: str,
        language: str,
        test_cases: list[TestCaseInput],
        entrypoint: str | None = None,
        timeout_seconds: float = 2.0,
        memory_limit_mb: int = 512,
    ) -> ExecutionResult:
        """Dispatch execution request to corresponding language runner."""
        lang_key = language.lower().strip()
        runner = self._runners.get(lang_key)

        if not runner:
            supported = ", ".join(self.get_supported_languages())
            err_msg = f"Unsupported language '{language}'. Supported languages: {supported}"
            raise ValueError(err_msg)

        return await runner.run(
            code=code,
            test_cases=test_cases,
            entrypoint=entrypoint,
            timeout_seconds=timeout_seconds,
            memory_limit_mb=memory_limit_mb,
        )


execution_engine = ExecutionEngine()
