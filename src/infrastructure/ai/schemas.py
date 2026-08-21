"""AI Foundation data models and schemas."""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class TaskType(str, Enum):
    """AI Task classification enum."""

    SOCRATIC_TUTOR = "SOCRATIC_TUTOR"
    CODE_REVIEW = "CODE_REVIEW"
    COMPLEXITY_ANALYSIS = "COMPLEXITY_ANALYSIS"
    HINT_GENERATION = "HINT_GENERATION"
    GENERAL_QA = "GENERAL_QA"


class LLMMessage(BaseModel):
    """Single turn message in LLM conversation context."""

    role: str = Field(..., description="Role of message sender ('system', 'user', 'assistant')")
    content: str = Field(..., description="Message body content")


class LLMResponse(BaseModel):
    """Response returned from LLM provider."""

    model_config = ConfigDict(protected_namespaces=())

    content: str = Field(..., description="Generated message response text")
    model_name: str = Field(..., description="Model identifier used for generation")
    provider_name: str = Field(..., description="Provider identifier ('openai', 'anthropic', 'mock')")
    prompt_tokens: int = Field(default=0, description="Tokens used in prompt")
    completion_tokens: int = Field(default=0, description="Tokens used in completion")
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    latency_ms: float = Field(default=0.0, description="Round-trip generation latency in milliseconds")
    finish_reason: str = Field(default="stop", description="Generation termination reason")


class GuardrailValidationResult(BaseModel):
    """Result of prompt injection defense or PII sanitization."""

    is_safe: bool = Field(..., description="Whether prompt passed all safety guardrails")
    flagged_reasons: list[str] = Field(default_factory=list, description="List of detected safety violations")
    sanitized_prompt: str = Field(..., description="Sanitized prompt content with redacted PII")
    risk_score: float = Field(default=0.0, description="Risk level metric between 0.0 (safe) and 1.0 (malicious)")
