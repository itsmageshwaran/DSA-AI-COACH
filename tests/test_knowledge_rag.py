"""Unit and integration test suite for Vector Store, Hybrid RAG Retriever, Memory Store, and Knowledge APIs."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient

from src.infrastructure.memory.store import memory_store
from src.infrastructure.rag.retriever import rag_retriever
from src.infrastructure.vector.embeddings import cosine_similarity, embedding_service
from src.infrastructure.vector.schemas import VectorDocument
from src.infrastructure.vector.store import InMemoryVectorStore


def test_embedding_service_and_cosine_similarity() -> None:
    """Verify EmbeddingService output dimension and cosine similarity math."""
    v1 = embedding_service.generate_embedding("two sum array search")
    v2 = embedding_service.generate_embedding("two sum array search")
    v3 = embedding_service.generate_embedding("completely unrelated text string")

    assert len(v1) == 128
    assert abs(cosine_similarity(v1, v2) - 1.0) < 1e-4
    assert cosine_similarity(v1, v3) < 1.0


@pytest.mark.anyio
async def test_in_memory_vector_store() -> None:
    """Verify InMemoryVectorStore document addition and vector similarity search."""
    store = InMemoryVectorStore()
    docs = [
        VectorDocument(id="1", text="Binary search on sorted array"),
        VectorDocument(id="2", text="Depth first search on graph tree"),
    ]
    await store.add_documents(docs)

    results = await store.search("binary search", top_k=1)
    assert len(results) == 1
    assert results[0].document.id == "1"


@pytest.mark.anyio
async def test_hybrid_rag_retriever() -> None:
    """Verify HybridRAGRetriever combines dense similarity and keyword matching."""
    results = await rag_retriever.retrieve("sliding window contiguous array", top_k=2)
    assert len(results) > 0
    top_doc = results[0].document
    assert "Sliding Window" in top_doc.text or "doc_sliding_window" in top_doc.id


def test_conversation_memory_store() -> None:
    """Verify ConversationMemoryStore turns accumulation and sliding window summarization."""
    session_id = "test_sess_100"
    memory_store.clear(session_id)

    memory_store.add_turn(session_id, "user", "What is Big-O?")
    memory_store.add_turn(session_id, "assistant", "Big-O characterizes upper bound execution time.")
    memory_store.add_turn(session_id, "user", "Give me an example.")
    memory_store.add_turn(session_id, "assistant", "O(N) for linear array scan.")

    history = memory_store.get_history(session_id)
    assert len(history) == 4

    # Add extra turns to trigger window threshold
    for i in range(5):
        memory_store.add_turn(session_id, "user", f"Followup question {i}")
        memory_store.add_turn(session_id, "assistant", f"Answer {i}")

    context = memory_store.get_summarized_context(session_id, max_turns=4)
    assert "Summary of previous" in context
    assert "User: Followup question 4" in context


@pytest.mark.anyio
async def test_knowledge_api_search(client: AsyncClient) -> None:
    """Verify POST /api/v1/knowledge/search endpoint."""
    payload = {
        "query": "Hash map O(1) lookup",
        "top_k": 2,
    }
    response = await client.post("/api/v1/knowledge/search", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
    assert data["query"] == payload["query"]


@pytest.mark.anyio
async def test_knowledge_api_index(client: AsyncClient) -> None:
    """Verify POST /api/v1/knowledge/index endpoint."""
    payload = {
        "id": "custom_doc_101",
        "text": "Trie prefix tree data structure for autocomplete string search.",
        "metadata": {"concept": "Trees", "topic": "Trie"},
    }
    response = await client.post("/api/v1/knowledge/index", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["indexed_id"] == "custom_doc_101"
    assert data["status"] == "success"
