"""Hybrid RAG retriever combining dense vector search with BM25 keyword matching."""

from __future__ import annotations

from src.infrastructure.vector.schemas import SearchResult, VectorDocument
from src.infrastructure.vector.store import vector_store

CANONICAL_DSA_DOCUMENTS = [
    VectorDocument(
        id="doc_two_pointers",
        text=(
            "Two Pointer Technique: Use two index pointers moving towards each other or at varying speeds "
            "to solve array search and subarray problems in O(N) time complexity instead of O(N^2)."
        ),
        metadata={"concept": "Arrays", "topic": "Two Pointers", "difficulty": "Easy"},
    ),
    VectorDocument(
        id="doc_sliding_window",
        text=(
            "Sliding Window Pattern: Maintain a running window frame over a contiguous subarray or string. "
            "Expand right pointer to satisfy conditions, shrink left pointer. "
            "Useful for min/max subarray problems."
        ),
        metadata={"concept": "Arrays", "topic": "Sliding Window", "difficulty": "Medium"},
    ),
    VectorDocument(
        id="doc_hash_map",
        text=(
            "Hash Map Lookup: Store key-value pairs to achieve average O(1) time complexity search. "
            "Ideal for complement lookups like Two Sum, frequency counting, and anagram checking."
        ),
        metadata={"concept": "Hash Tables", "topic": "Hash Map", "difficulty": "Easy"},
    ),
    VectorDocument(
        id="doc_binary_search",
        text=(
            "Binary Search: Divide search interval in half repeatedly on sorted arrays. "
            "Operates in O(log N) time. Remember to check mid element, low, and high pointer bounds."
        ),
        metadata={"concept": "Searching", "topic": "Binary Search", "difficulty": "Easy"},
    ),
    VectorDocument(
        id="doc_bfs_dfs",
        text=(
            "Graph BFS and DFS Traversal: Breadth-First Search uses a Queue for shortest path problems. "
            "Depth-First Search uses recursion/Stack for topological sorting and cycle detection. O(V + E) complexity."
        ),
        metadata={"concept": "Graphs", "topic": "BFS/DFS", "difficulty": "Medium"},
    ),
]


class HybridRAGRetriever:
    """Hybrid RAG retriever combining dense vector search and keyword match scoring."""

    def __init__(self) -> None:
        self.store = vector_store
        self._is_seeded = False

    async def seed_knowledge_base(self) -> None:
        """Seed vector store with canonical DSA knowledge documents if empty."""
        if not self._is_seeded:
            await self.store.add_documents(CANONICAL_DSA_DOCUMENTS)
            self._is_seeded = True

    def calculate_keyword_score(self, query: str, doc_text: str) -> float:
        """Calculate BM25-like keyword overlap score."""
        query_words = set(query.lower().split())
        doc_words = doc_text.lower().split()
        if not query_words or not doc_words:
            return 0.0

        matches = sum(1 for w in doc_words if w in query_words)
        return min(1.0, matches / max(1, len(query_words)))

    async def retrieve(self, query: str, top_k: int = 3) -> list[SearchResult]:
        """Perform hybrid RAG retrieval combining dense vector similarity and keyword score."""
        await self.seed_knowledge_base()

        vector_results = await self.store.search(query, top_k=top_k * 2)
        hybrid_results: list[SearchResult] = []

        for res in vector_results:
            kw_score = self.calculate_keyword_score(query, res.document.text)
            # Weighted ensemble score: 0.7 vector similarity + 0.3 keyword match
            hybrid_score = round(0.7 * res.score + 0.3 * kw_score, 4)
            hybrid_results.append(SearchResult(document=res.document, score=hybrid_score))

        hybrid_results.sort(key=lambda r: r.score, reverse=True)
        return hybrid_results[:top_k]


rag_retriever = HybridRAGRetriever()
