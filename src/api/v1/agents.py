"""FastAPI router for Autonomous Agent execution and tool registry endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status

from src.modules.agents.schemas import AgentRunRequest, AgentRunResponse
from src.modules.agents.service import agent_service

router = APIRouter()


@router.post(
    "/run",
    name="agents-run",
    status_code=status.HTTP_200_OK,
    response_model=AgentRunResponse,
    tags=["Agent Framework"],
)
async def run_agent(
    request: AgentRunRequest,
) -> AgentRunResponse:
    """Run autonomous agent graph orchestrator loop."""
    return await agent_service.run_agent(request)


@router.get(
    "/tools",
    name="agents-tools",
    status_code=status.HTTP_200_OK,
    tags=["Agent Framework"],
)
async def list_tools() -> list[dict[str, Any]]:
    """List registered platform tools and their argument JSON schemas."""
    return agent_service.list_tools()
