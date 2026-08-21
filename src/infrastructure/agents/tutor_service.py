"""Tutor Service for Multi-Agent Socratic Guidance."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from src.infrastructure.ai.gateway import ai_gateway
from src.infrastructure.ai.schemas import LLMMessage, TaskType


class TutorService:
    """Coordinates multi-agent Socratic guidance over streaming connections."""

    def __init__(self) -> None:
        self.gateway = ai_gateway
        self.conversation_history: list[dict[str, str]] = []

    async def handle_message(self, message: str, context: dict[str, Any] | None = None) -> AsyncGenerator[str, None]:
        """Handle an incoming message and stream back the response.

        Args:
            message: The user's input message.
            context: Optional context dict with course_id, lesson_id, etc.

        """
        self.conversation_history.append({"role": "user", "content": message})

        # Prepare context for prompt
        system_context = ""
        if context:
            system_context = f"\nContext:\n{json.dumps(context, indent=2)}"

        messages = [
            LLMMessage(role="system", content=f"You are a helpful tutor.{system_context}"),
            *[LLMMessage(**m) for m in self.conversation_history],
        ]

        full_response = ""
        async for chunk in self.gateway.generate_stream(
            messages=messages,
            task_type=TaskType.SOCRATIC_TUTOR,
        ):
            full_response += chunk
            yield chunk

        self.conversation_history.append({"role": "assistant", "content": full_response})

    async def _stream_agent_response(
        self,
        system_prompt: str,
        user_prompt: str,
        context: dict | None = None
    ) -> AsyncGenerator[str, None]:
        """Stream response from a specific agent prompt."""
        if context:
            system_prompt += f"\nContext:\n{json.dumps(context, indent=2)}"
            
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        async for chunk in self.gateway.generate_stream(
            messages=messages,
            task_type=TaskType.SOCRATIC_TUTOR,
        ):
            yield chunk

    async def socratic_guide_stream(
        self, code: str, execution_result: dict | None, ast_analysis: dict | None, context: dict | None = None
    ) -> AsyncGenerator[str, None]:
        """Socratic Guide Agent: Asks focused, low cognitive load diagnostic counter-questions."""
        system_prompt = (
            "You are the Socratic DSA Coach. Your mission is to help the student solve algorithmic problems "
            "themselves with maximum clarity and MINIMAL cognitive load.\n\n"
            "CRITICAL RULES:\n"
            "1. NEVER output internal monologues, preamble ('We need to...', 'Let me think...'), or restate the full problem.\n"
            "2. DO NOT write the complete solution or full code.\n"
            "3. Keep your total response under 100 words. Be encouraging, concise, and punchy.\n"
            "4. Structure your response in exactly 3 clean visual blocks:\n"
            "   - 💡 **Observation**: 1 punchy sentence about where they currently are or what the code is doing.\n"
            "   - 🎯 **Key Question**: 1 single, thought-provoking question to unlock the next logical step.\n"
            "   - ⚡ **Hint**: 1 small hint (e.g., mention a data structure, lookup technique, or edge case)."
        )
        user_prompt = f"Student's Current Code:\n```python\n{code}\n```\n"
        if execution_result:
            user_prompt += f"Execution Feedback: {json.dumps(execution_result.get('status') or execution_result.get('error') or 'Tested')}\n"
        if ast_analysis:
            user_prompt += f"AST Complexity Estimate: {json.dumps(ast_analysis)}\n"

        async for chunk in self._stream_agent_response(system_prompt, user_prompt, context):
            yield chunk

    async def code_auditor_stream(self, code: str, ast_analysis: dict | None, context: dict | None = None) -> AsyncGenerator[str, None]:
        """Code Auditor Agent: Evaluates code structure and edge cases cleanly."""
        system_prompt = (
            "You are the Code Auditor Agent. Spot structural flaws and edge cases with minimal cognitive load.\n\n"
            "CRITICAL RULES:\n"
            "1. NO internal reasoning or meta-commentary.\n"
            "2. Keep the answer under 90 words.\n"
            "3. Structure with 2 bullet points:\n"
            "   - 🔍 **Vulnerability / Inefficiency**: Point out 1 potential bug or bottleneck.\n"
            "   - 🛡️ **Edge Case to Check**: Name 1 specific input to test (e.g., negative numbers, empty input)."
        )
        user_prompt = f"Code:\n```python\n{code}\n```\n"
        if ast_analysis:
            user_prompt += f"AST Findings: {json.dumps(ast_analysis)}\n"

        async for chunk in self._stream_agent_response(system_prompt, user_prompt, context):
            yield chunk

    async def complexity_analyst_stream(self, code: str, context: dict | None = None) -> AsyncGenerator[str, None]:
        """Complexity Analyst Agent: Analyzes time/space complexity concisely."""
        system_prompt = (
            "You are the Complexity Analyst Agent. Give instant, crystal-clear Big-O complexity feedback.\n\n"
            "CRITICAL RULES:\n"
            "1. NO internal monologue.\n"
            "2. Format strictly as:\n"
            "   - ⏱️ **Time Complexity**: Big-O with 1 short sentence explaining why.\n"
            "   - 💾 **Space Complexity**: Big-O with 1 short sentence explaining why.\n"
            "   - 🚀 **Target Optimal**: What Big-O is expected for top tech interviews on this problem."
        )
        user_prompt = f"Code:\n```python\n{code}\n```\n"

        async for chunk in self._stream_agent_response(system_prompt, user_prompt, context):
            yield chunk


tutor_service = TutorService()
