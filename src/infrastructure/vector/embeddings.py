"""Embedding generator and vector math utilities."""

from __future__ import annotations

import math
import hashlib


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Calculate cosine similarity score between two dense vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(v1, v2, strict=False))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class EmbeddingService:
    """Dense vector embedding service producing 128-dim normalized embeddings."""

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension

    def generate_embedding(self, text: str) -> list[float]:
        """Generate deterministic pseudo-random 128-dim normalized embedding vector."""
        if not text:
            return [0.0] * self.dimension

        # Generate deterministic floats from SHA-256 hash stream
        vector: list[float] = []
        for i in range(self.dimension):
            seed = f"{text}:{i}"
            digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
            # Map hex integer to range [-1.0, 1.0]
            val = (int(digest[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
            vector.append(val)

        # L2 normalize vector
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector


embedding_service = EmbeddingService()
