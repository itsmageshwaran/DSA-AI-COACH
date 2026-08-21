"""Prompt templates for Socratic tutoring, code review, and complexity analysis."""

from __future__ import annotations

from src.infrastructure.ai.schemas import LLMMessage

SOCRATIC_TUTOR_SYSTEM = """You are a Principal AI Coach specializing in Data Structures & Algorithms (DSA).
Your core mission is to guide learners using the Socratic method.

RULES:
1. NEVER output direct complete code solutions unless explicitly requested by an admin.
2. Ask targeted diagnostic questions about the learner's logic, edge cases, or pointer states.
3. Keep hints concise, encouraging, and focused on building intuitive understanding.
"""

CODE_REVIEW_SYSTEM = """You are a Principal Software Architect auditing student DSA solutions.
Focus on:
1. Correctness & Edge case vulnerabilities (empty lists, negative values, integer overflow).
2. Clean code principles & variable naming.
3. Idiomatic performance improvements.
"""

COMPLEXITY_ANALYSIS_SYSTEM = """You are a Theoretical Computer Scientist analyzing algorithm efficiency.
Analyze:
1. Worst-case and Average-case Time Complexity in Big-O notation.
2. Auxiliary Space Complexity in Big-O notation.
3. Key loops or recursive call stack frames driving the complexity.
"""

HINT_GENERATION_SYSTEM = """You are an AI Tutor crafting progressive hints for DSA exercises.
Provide a progressive hint matching the requested hint tier (Tier 1: conceptual nudge, Tier 2: data structure).
Do not reveal full code implementations.
"""


class PromptTemplate:
    """Type-safe prompt template formatter."""

    def __init__(self, system_prompt: str, user_template: str) -> None:
        self.system_prompt = system_prompt
        self.user_template = user_template

    def format_messages(self, **kwargs: str) -> list[LLMMessage]:
        """Format system and user messages with keyword arguments."""
        formatted_user = self.user_template.format(**kwargs)
        return [
            LLMMessage(role="system", content=self.system_prompt),
            LLMMessage(role="user", content=formatted_user),
        ]


socratic_user_template = (
    "Exercise: {exercise_title}\n"
    "Concept: {concept_name}\n"
    "Code:\n{code}\n"
    "Execution Error/Output:\n{execution_output}\n"
    "Learner Question: {user_query}"
)

socratic_tutor_template = PromptTemplate(
    system_prompt=SOCRATIC_TUTOR_SYSTEM,
    user_template=socratic_user_template,
)

code_review_template = PromptTemplate(
    system_prompt=CODE_REVIEW_SYSTEM,
    user_template="Language: {language}\nCode Submission:\n{code}",
)

complexity_analysis_template = PromptTemplate(
    system_prompt=COMPLEXITY_ANALYSIS_SYSTEM,
    user_template="Algorithm Code:\n{code}",
)

hint_template = PromptTemplate(
    system_prompt=HINT_GENERATION_SYSTEM,
    user_template="Exercise: {exercise_title}\nHint Tier: {hint_tier}\nCurrent Code:\n{code}",
)
