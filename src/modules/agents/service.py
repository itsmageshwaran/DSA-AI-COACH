"""Agent Application Service managing autonomous state graphs and tool discovery."""

from __future__ import annotations

from typing import Any

from src.infrastructure.agents.orchestrator import agent_orchestrator
from src.infrastructure.agents.state import AgentState
from src.infrastructure.agents.tools.registry import tool_registry
from src.modules.agents.schemas import AgentRunRequest, AgentRunResponse


class AgentService:
    """Application Service for Autonomous Agent execution and tool discovery."""

    async def run_agent(self, request: AgentRunRequest) -> AgentRunResponse:
        """Run autonomous agent state graph orchestrator."""
        initial_state = AgentState(
            session_id=request.session_id,
            task_prompt=request.task_prompt,
            code=request.code,
            language=request.language,
            max_iterations=request.max_iterations,
        )

        final_state = await agent_orchestrator.run(initial_state)

        return AgentRunResponse(
            final_output=final_state.final_output,
            iterations_used=final_state.iteration_count,
            state=final_state,
        )

    def list_tools(self) -> list[dict[str, Any]]:
        """List registered agent tools."""
        return tool_registry.list_tools()


agent_service = AgentService()
