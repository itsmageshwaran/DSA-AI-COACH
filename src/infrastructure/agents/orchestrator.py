"""Autonomous Agent Orchestrator managing tool execution loops and AI Gateway synthesis."""

from __future__ import annotations

from src.infrastructure.agents.state import AgentState
from src.infrastructure.agents.tools.registry import tool_registry
from src.infrastructure.ai.gateway import ai_gateway
from src.infrastructure.ai.schemas import LLMMessage, TaskType


class AgentOrchestrator:
    """Orchestrates multi-perspective autonomous agent state loops using platform tools."""

    def __init__(self) -> None:
        self.tools = tool_registry
        self.gateway = ai_gateway

    async def run(self, state: AgentState) -> AgentState:
        """Execute state machine graph loop until task completion or max_iterations limit."""
        while not state.is_complete and state.iteration_count < state.max_iterations:
            state.iteration_count += 1

            if state.code and state.ast_analysis is None:
                ast_res = await self.tools.execute_tool("inspect_ast", {"code": state.code})
                state.ast_analysis = ast_res.data if ast_res.success else {"is_safe": False}

            if state.code and state.execution_result is None:
                exec_res = await self.tools.execute_tool(
                    "execute_code", {"code": state.code, "language": state.language}
                )
                state.execution_result = exec_res.data if exec_res.success else {"status": "error"}

            if not state.rag_context:
                rag_res = await self.tools.execute_tool("retrieve_knowledge", {"query": state.task_prompt, "top_k": 2})
                if rag_res.success and isinstance(rag_res.data, dict):
                    state.rag_context = rag_res.data.get("results", [])

            system_prompt = (
                "You are an Autonomous AI Engineering Coach. Synthesize execution results, "
                "AST findings, and RAG knowledge into a Socratic response."
            )

            prompt_body = (
                f"Task Goal: {state.task_prompt}\n"
                f"Code:\n{state.code}\n"
                f"AST Findings: {state.ast_analysis}\n"
                f"Execution Output: {state.execution_result}\n"
                f"Knowledge Context: {state.rag_context}\n"
            )

            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=prompt_body),
            ]

            llm_res = await self.gateway.generate(
                messages=messages,
                task_type=TaskType.SOCRATIC_TUTOR,
                temperature=0.7,
                max_tokens=600,
            )

            state.final_output = llm_res.content
            state.is_complete = True

        return state


agent_orchestrator = AgentOrchestrator()
