"""Agent execution state machine context."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Autonomous agent execution state graph context."""

    session_id: str = Field(..., description="Session or user identifier")
    task_prompt: str = Field(..., description="Goal instruction for the agent")
    code: str = Field(default="", description="Learner code snippet")
    language: str = Field(default="python", description="Target programming language")

    # Pipeline execution state
    ast_analysis: dict[str, Any] | None = Field(default=None, description="AST security & structural analysis data")
    execution_result: dict[str, Any] | None = Field(default=None, description="Sandbox runtime execution data")
    rag_context: list[dict[str, Any]] = Field(default_factory=list, description="Retrieved RAG knowledge articles")

    # Orchestration metadata
    iteration_count: int = Field(default=0, description="Loop iteration counter")
    max_iterations: int = Field(default=5, description="Maximum allowed loop iterations")
    is_complete: bool = Field(default=False, description="Flag indicating goal completion")
    final_output: str = Field(default="", description="Final synthesized agent output string")
