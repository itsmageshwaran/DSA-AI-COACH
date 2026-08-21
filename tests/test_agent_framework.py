"""Unit and integration test suite for Agent Tools, Agent Tool Registry, Agent Orchestrator, and Agent APIs."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient

from src.infrastructure.agents.orchestrator import agent_orchestrator
from src.infrastructure.agents.state import AgentState
from src.infrastructure.agents.tools.code_tools import ExecuteCodeTool, InspectASTTool
from src.infrastructure.agents.tools.knowledge_tools import RetrieveKnowledgeTool
from src.infrastructure.agents.tools.registry import tool_registry


def test_tool_registry_list_and_lookup() -> None:
    """Verify AgentToolRegistry lists default tools and retrieves strategies by name."""
    tools = tool_registry.list_tools()
    assert len(tools) >= 4
    tool_names = {t["name"] for t in tools}
    assert "execute_code" in tool_names
    assert "inspect_ast" in tool_names
    assert "evaluate_test_cases" in tool_names
    assert "retrieve_knowledge" in tool_names

    tool_inst = tool_registry.get_tool("execute_code")
    assert tool_inst is not None
    assert tool_inst.name == "execute_code"


@pytest.mark.anyio
async def test_execute_code_tool() -> None:
    """Verify ExecuteCodeTool executes Python code in sandbox."""
    tool = ExecuteCodeTool()
    res = await tool.execute(code="def main(x=1):\n    print('Agent Tool Test')\n    return x", language="python")
    assert res.success is True
    assert res.data["status"] == "ACCEPTED"


@pytest.mark.anyio
async def test_inspect_ast_tool() -> None:
    """Verify InspectASTTool performs static AST analysis."""
    tool = InspectASTTool()
    res = await tool.execute(code="def foo():\n    for i in range(5):\n        pass")
    assert res.success is True
    assert res.data["max_loop_nesting_depth"] == 1
    assert "foo" in res.data["function_names"]


@pytest.mark.anyio
async def test_retrieve_knowledge_tool() -> None:
    """Verify RetrieveKnowledgeTool retrieves canonical RAG articles."""
    tool = RetrieveKnowledgeTool()
    res = await tool.execute(query="Binary search on sorted array", top_k=2)
    assert res.success is True
    assert res.data["count"] > 0


@pytest.mark.anyio
async def test_agent_orchestrator_run() -> None:
    """Verify AgentOrchestrator state graph loop execution."""
    sample_code = (
        "def two_sum(nums, target):\n"
        "    for i in range(len(nums)):\n"
        "        for j in range(len(nums)):\n"
        "            if nums[i] + nums[j] == target:\n"
        "                return [i, j]"
    )

    initial_state = AgentState(
        session_id="agent_sess_1",
        task_prompt="How do I fix the inner loop in my two sum code?",
        code=sample_code,
    )

    final_state = await agent_orchestrator.run(initial_state)
    assert final_state.is_complete is True
    assert final_state.iteration_count > 0
    assert len(final_state.final_output) > 0
    assert final_state.ast_analysis is not None
    assert final_state.execution_result is not None


@pytest.mark.anyio
async def test_agent_api_run(client: AsyncClient) -> None:
    """Verify POST /api/v1/agents/run endpoint."""
    payload = {
        "task_prompt": "Help me optimize two sum",
        "code": "def two_sum(nums, target):\n    return []",
    }
    response = await client.post("/api/v1/agents/run", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "final_output" in data
    assert data["iterations_used"] > 0
    assert data["state"]["is_complete"] is True


@pytest.mark.anyio
async def test_agent_api_tools(client: AsyncClient) -> None:
    """Verify GET /api/v1/agents/tools endpoint."""
    response = await client.get("/api/v1/agents/tools")
    assert response.status_code == status.HTTP_200_OK

    tools_list = response.json()
    assert isinstance(tools_list, list)
    assert len(tools_list) >= 4
