"""Vector Store implementations supporting dense vector similarity search."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.infrastructure.vector.embeddings import cosine_similarity, embedding_service
from src.infrastructure.vector.schemas import SearchResult, VectorDocument


class BaseVectorStore(ABC):
    """Abstract Vector Store interface."""

    @abstractmethod
    async def add_documents(self, documents: list[VectorDocument]) -> None:
        """Add documents to vector index."""

    @abstractmethod
    async def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        """Search vector store by similarity to query text."""


class InMemoryVectorStore(BaseVectorStore):
    """In-Memory vector store implementation for lightweight RAG retrieval."""

    def __init__(self) -> None:
        self._documents: dict[str, VectorDocument] = {}

    async def add_documents(self, documents: list[VectorDocument]) -> None:
        """Add documents and ensure embeddings are populated."""
        for doc in documents:
            if not doc.embedding:
                doc.embedding = embedding_service.generate_embedding(doc.text)
            self._documents[doc.id] = doc

    async def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        """Perform cosine similarity vector search over indexed documents."""
        if not self._documents:
            return []

        query_vector = embedding_service.generate_embedding(query)
        results: list[SearchResult] = []

        for doc in self._documents.values():
            score = cosine_similarity(query_vector, doc.embedding)
            results.append(SearchResult(document=doc, score=round(score, 4)))

        # Sort descending by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]


vector_store = InMemoryVectorStore()
