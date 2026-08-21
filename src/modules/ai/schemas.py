"""AI Application request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.infrastructure.ai.schemas import (
    GuardrailValidationResult,
    LLMResponse,
    TaskType,
)


class AIGenerateRequest(BaseModel):
    """Request payload for general AI completion."""

    prompt: str = Field(..., description="User prompt text", min_length=1)
    task_type: TaskType | None = Field(default=None, description="Task classification type")
    provider: str | None = Field(default=None, description="Provider override ('openai', 'mock')")
    model: str | None = Field(default=None, description="Model override")
    system_prompt: str | None = Field(default=None, description="Optional system prompt")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=1000, ge=1, le=4096, description="Max tokens limit")


class AIGenerateResponse(BaseModel):
    """Response payload for general AI completion."""

    response: LLMResponse
    guardrail: GuardrailValidationResult


class SocraticHintRequest(BaseModel):
    """Request payload for generating Socratic hints."""

    exercise_title: str = Field(..., description="Title of exercise problem")
    concept_name: str = Field(..., description="Target DSA concept topic")
    code: str = Field(..., description="Learner current code submission")
    execution_output: str = Field(default="", description="Output stdout/stderr or test error message")
    user_query: str = Field(default="Where is the bug in my code?", description="Learner question")


class SocraticHintResponse(BaseModel):
    """Response payload for Socratic hint generation."""

    hint: str
    task_type: TaskType = TaskType.SOCRATIC_TUTOR
    llm_response: LLMResponse
