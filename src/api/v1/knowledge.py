"""FastAPI router for Knowledge Base RAG search and vector indexing."""

from __future__ import annotations

from fastapi import APIRouter, status

from src.modules.knowledge.schemas import (
    KnowledgeIndexRequest,
    KnowledgeIndexResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from src.modules.knowledge.service import knowledge_service

router = APIRouter()


@router.post(
    "/search",
    name="knowledge-search",
    status_code=status.HTTP_200_OK,
    response_model=KnowledgeSearchResponse,
    tags=["Knowledge RAG"],
)
async def search_knowledge(
    request: KnowledgeSearchRequest,
) -> KnowledgeSearchResponse:
    """Perform hybrid RAG semantic search over canonical DSA knowledge base."""
    return await knowledge_service.search_knowledge(request)


@router.post(
    "/index",
    name="knowledge-index",
    status_code=status.HTTP_201_CREATED,
    response_model=KnowledgeIndexResponse,
    tags=["Knowledge RAG"],
)
async def index_document(
    request: KnowledgeIndexRequest,
) -> KnowledgeIndexResponse:
    """Index a new article or editorial into vector store."""
    return await knowledge_service.index_document(request)
