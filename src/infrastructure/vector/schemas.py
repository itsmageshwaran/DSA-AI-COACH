"""Vector Store schemas and data models."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class VectorDocument(BaseModel):
    """Document indexed inside vector store."""

    id: str = Field(..., description="Unique document ID")
    text: str = Field(..., description="Raw text content of document")
    embedding: list[float] = Field(default_factory=list, description="Dense vector embedding")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")


class SearchResult(BaseModel):
    """Vector similarity search result item."""

    document: VectorDocument
    score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
