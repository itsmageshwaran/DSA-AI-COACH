"""Agent Tool Registry managing tool discovery and execution."""

from __future__ import annotations

from typing import Any

from src.infrastructure.agents.tools.base import BaseTool, ToolResult
from src.infrastructure.agents.tools.code_tools import (
    EvaluateTestCasesTool,
    ExecuteCodeTool,
    InspectASTTool,
)
from src.infrastructure.agents.tools.knowledge_tools import RetrieveKnowledgeTool


class AgentToolRegistry:
    """Registry maintaining available agent tool strategies."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        # Register standard default platform tools
        self.register(ExecuteCodeTool())
        self.register(InspectASTTool())
        self.register(EvaluateTestCasesTool())
        self.register(RetrieveKnowledgeTool())

    def register(self, tool: BaseTool) -> None:
        """Register tool strategy."""
        self._tools[tool.name.lower()] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        """Get tool strategy by name."""
        return self._tools.get(name.lower())

    def list_tools(self) -> list[dict[str, Any]]:
        """List registered tools with JSON schema descriptions."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters_schema": t.parameters_schema,
            }
            for t in self._tools.values()
        ]

    async def execute_tool(self, name: str, kwargs: dict[str, Any]) -> ToolResult:
        """Dispatch execution to registered tool."""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                tool_name=name,
                success=False,
                error=f"Tool '{name}' not found in AgentToolRegistry.",
            )
        return await tool.execute(**kwargs)


tool_registry = AgentToolRegistry()
