"""Execution engine data models and schemas."""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """Execution status enum representing problem evaluation outcome."""

    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    SYSTEM_ERROR = "SYSTEM_ERROR"


class TestCaseInput(BaseModel):
    """Input test case schema."""

    __test__ = False

    input_data: dict[str, Any] | list[Any] | str = Field(
        ..., description="Inputs provided to entrypoint function (dict of kwargs or list of positional args)"
    )
    expected_output: Any = Field(..., description="Expected output returned by function")
    is_hidden: bool = Field(default=False, description="Whether test case is hidden from learner preview")


class TestCaseResult(BaseModel):
    """Result of running a single test case."""

    __test__ = False

    test_case_index: int
    passed: bool
    input_data: Any
    expected_output: Any
    actual_output: Any = None
    stdout: str = ""
    stderr: str = ""
    runtime_ms: float = 0.0
    memory_kb: float = 0.0
    status: ExecutionStatus = ExecutionStatus.ACCEPTED
    error_message: str | None = None
    is_hidden: bool = False


class ASTAnalysisResult(BaseModel):
    """Result of static AST code analysis."""

    is_valid: bool
    syntax_error: str | None = None
    forbidden_imports: list[str] = Field(default_factory=list)
    nesting_depth: int = 0
    has_recursion: bool = False
    function_names: list[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    """Overall execution result across all evaluated test cases."""

    status: ExecutionStatus
    passed_count: int
    total_count: int
    pass_rate: float
    avg_runtime_ms: float
    peak_memory_kb: float
    test_results: list[TestCaseResult] = Field(default_factory=list)
    ast_analysis: ASTAnalysisResult | None = None
    compilation_output: str = ""
