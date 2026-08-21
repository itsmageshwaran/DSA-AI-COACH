"""Knowledge RAG Application request and response schemas."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from src.infrastructure.vector.schemas import SearchResult


class KnowledgeSearchRequest(BaseModel):
    """Request payload for semantic RAG knowledge search."""

    query: str = Field(..., description="Natural language search query", min_length=1)
    top_k: int = Field(default=3, ge=1, le=10, description="Max search result count")


class KnowledgeSearchResponse(BaseModel):
    """Response payload for semantic RAG knowledge search."""

    query: str
    results: list[SearchResult]


class KnowledgeIndexRequest(BaseModel):
    """Request payload for indexing a new knowledge document into vector store."""

    id: str = Field(..., description="Unique document ID")
    text: str = Field(..., description="Text body of document", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata key-values")


class KnowledgeIndexResponse(BaseModel):
    """Response payload for indexing document."""

    indexed_id: str
    status: str = "success"
