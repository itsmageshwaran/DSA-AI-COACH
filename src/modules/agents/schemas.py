"""Agents request and response schemas."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from src.infrastructure.agents.state import AgentState


class AgentRunRequest(BaseModel):
    """Request payload for running autonomous agent graph loop."""

    task_prompt: str = Field(..., description="Goal instruction or query for the agent", min_length=1)
    code: str = Field(default="", description="Learner code snippet")
    language: str = Field(default="python", description="Target programming language")
    session_id: str = Field(default="default_session", description="Session identifier")
    max_iterations: int = Field(default=5, ge=1, le=10, description="Max loop iteration safety boundary")


class AgentRunResponse(BaseModel):
    """Response payload for autonomous agent graph run."""

    final_output: str
    iterations_used: int
    state: AgentState


class AgentToolItem(BaseModel):
    """Registered agent tool metadata item."""

    name: str
    description: str
    parameters_schema: dict[str, Any]
