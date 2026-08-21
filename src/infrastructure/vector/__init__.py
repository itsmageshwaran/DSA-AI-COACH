"""Vector Infrastructure package."""

from src.infrastructure.vector.embeddings import EmbeddingService, cosine_similarity, embedding_service
from src.infrastructure.vector.schemas import SearchResult, VectorDocument
from src.infrastructure.vector.store import BaseVectorStore, InMemoryVectorStore, vector_store

__all__ = [
    "BaseVectorStore",
    "EmbeddingService",
    "InMemoryVectorStore",
    "SearchResult",
    "VectorDocument",
    "cosine_similarity",
    "embedding_service",
    "vector_store",
]
