"""Knowledge Application Service managing vector RAG search and indexing."""

from __future__ import annotations

from src.infrastructure.rag.retriever import rag_retriever
from src.infrastructure.vector.schemas import VectorDocument
from src.infrastructure.vector.store import vector_store
from src.modules.knowledge.schemas import (
    KnowledgeIndexRequest,
    KnowledgeIndexResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)


class KnowledgeService:
    """Application Service for Knowledge Base search and vector indexing."""

    async def search_knowledge(self, request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
        """Search canonical DSA knowledge base using hybrid vector RAG retriever."""
        results = await rag_retriever.retrieve(query=request.query, top_k=request.top_k)
        return KnowledgeSearchResponse(query=request.query, results=results)

    async def index_document(self, request: KnowledgeIndexRequest) -> KnowledgeIndexResponse:
        """Index new document into vector store."""
        doc = VectorDocument(
            id=request.id,
            text=request.text,
            metadata=request.metadata,
        )
        await vector_store.add_documents([doc])
        return KnowledgeIndexResponse(indexed_id=request.id, status="success")


knowledge_service = KnowledgeService()
