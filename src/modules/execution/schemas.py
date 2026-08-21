"""Execution API request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.infrastructure.execution.schemas import ExecutionResult, TestCaseInput


class ExecutionRunRequest(BaseModel):
    """Payload for running code against custom or sample test cases."""

    code: str = Field(..., description="Source code to execute", min_length=1)
    language: str = Field(
        default="python",
        description="Programming language ('python', 'javascript', 'cpp', 'java', 'go')",
    )
    test_cases: list[TestCaseInput] = Field(..., description="List of test cases to evaluate", min_length=1)
    entrypoint: str | None = Field(default=None, description="Name of the entrypoint function to invoke")


class ExecutionRunResponse(BaseModel):
    """Response payload for code execution run."""

    execution: ExecutionResult


class ExecutionSubmitRequest(BaseModel):
    """Payload for submitting exercise code solution."""

    exercise_id: str = Field(..., description="Target exercise ID")
    code: str = Field(..., description="Source code submission", min_length=1)
    language: str = Field(default="python", description="Programming language")
    entrypoint: str | None = Field(default=None, description="Entrypoint function name")
    custom_test_cases: list[TestCaseInput] | None = Field(default=None, description="Optional override test cases")


class ExecutionSubmitResponse(BaseModel):
    """Response payload for exercise code submission."""

    submission_id: str
    exercise_id: str
    status: str
    execution: ExecutionResult
    progress_updated: bool
    new_achievements: list = Field(default_factory=list, description="Newly unlocked achievements")
    mastery_update: dict | None = None
    next_problem: dict | None = None
