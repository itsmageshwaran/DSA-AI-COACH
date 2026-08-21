"""Abstract base class for Agent Tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Result of agent tool execution."""

    tool_name: str
    success: bool
    data: Any = Field(default=None, description="Output payload or return value")
    error: str | None = Field(default=None, description="Error message if execution failed")


class BaseTool(ABC):
    """Abstract Agent Tool interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name of the tool."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema of tool arguments."""

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute tool logic asynchronously."""
