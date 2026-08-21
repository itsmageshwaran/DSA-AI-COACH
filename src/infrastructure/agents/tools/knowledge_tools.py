"""Knowledge RAG retrieval agent tool."""

from __future__ import annotations

from typing import Any

from src.infrastructure.agents.tools.base import BaseTool, ToolResult
from src.infrastructure.rag.retriever import rag_retriever


class RetrieveKnowledgeTool(BaseTool):
    """Tool querying hybrid RAG retriever for canonical DSA knowledge documents."""

    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "retrieve_knowledge"

    @property
    def description(self) -> str:
        """Tool description."""
        return "Queries hybrid vector RAG store to retrieve canonical DSA solution patterns, algorithms, and hints."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Tool JSON schema parameters."""
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text describing topic or concept"},
                "top_k": {"type": "integer", "description": "Number of top results (default 3)"},
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute knowledge retrieval."""
        query = str(kwargs.get("query", ""))
        top_k = int(kwargs.get("top_k", 3))

        try:
            results = await rag_retriever.retrieve(query=query, top_k=top_k)
            retrieved_items = [
                {
                    "id": r.document.id,
                    "text": r.document.text,
                    "score": r.score,
                    "metadata": r.document.metadata,
                }
                for r in results
            ]
            return ToolResult(
                tool_name=self.name,
                success=True,
                data={
                    "query": query,
                    "count": len(retrieved_items),
                    "results": retrieved_items,
                },
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=str(e))
