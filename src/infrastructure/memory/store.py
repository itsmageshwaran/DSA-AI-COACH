"""Turn-by-turn conversation memory store with sliding-window context summarization."""

from __future__ import annotations

import time
import uuid
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    """Single turn item in conversation memory."""

    turn_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: float = Field(default_factory=time.time)


class ConversationMemoryStore:
    """In-memory sliding window conversation memory store."""

    def __init__(self) -> None:
        self._sessions: dict[str, list[ConversationTurn]] = {}

    def add_turn(self, session_id: str, role: str, content: str) -> ConversationTurn:
        """Append turn to session history."""
        turn = ConversationTurn(session_id=session_id, role=role, content=content)
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(turn)
        return turn

    def get_history(self, session_id: str, limit: int = 20) -> list[ConversationTurn]:
        """Retrieve recent conversation turns for session."""
        turns = self._sessions.get(session_id, [])
        return turns[-limit:]

    def get_summarized_context(self, session_id: str, max_turns: int = 6) -> str:
        """Format sliding window turns into context text with summary of older turns."""
        turns = self._sessions.get(session_id, [])
        if not turns:
            return ""

        if len(turns) <= max_turns:
            return "\n".join(f"{t.role.capitalize()}: {t.content}" for t in turns)

        # Separate older turns for summarization and recent turns for exact context
        older_turns = turns[:-max_turns]
        recent_turns = turns[-max_turns:]

        summary = (
            f"[Summary of previous {len(older_turns)} turns: "
            "Learner asked about DSA problem logic and received Socratic hints.]"
        )
        recent_context = "\n".join(f"{t.role.capitalize()}: {t.content}" for t in recent_turns)

        return f"{summary}\n{recent_context}"

    def clear(self, session_id: str) -> None:
        """Clear conversation memory for session."""
        if session_id in self._sessions:
            del self._sessions[session_id]


memory_store = ConversationMemoryStore()
