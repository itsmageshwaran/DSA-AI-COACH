"""Cache key generator helpers providing deterministic namespaces across the application."""

from __future__ import annotations

import hashlib


class CacheKey:
    """Namespace helpers for structured, deterministic Redis cache keys."""

    @staticmethod
    def session(session_id: str) -> str:
        """Format session cache key."""
        return f"dsa:session:{session_id}"

    @staticmethod
    def llm_response(prompt: str) -> str:
        """Generate MD5 hash cache key for LLM prompt responses."""
        prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()
        return f"dsa:llm_resp:{prompt_hash}"

    @staticmethod
    def prompt_template(name: str, version: str) -> str:
        """Format prompt template cache key."""
        return f"dsa:prompt:{name}:v{version}"

    @staticmethod
    def learning_progress(user_id: str) -> str:
        """Format user learning progress cache key."""
        return f"dsa:progress:{user_id}"

    @staticmethod
    def rate_limit(identifier: str, endpoint: str) -> str:
        """Format API rate limit key."""
        clean_endpoint = endpoint.strip("/").replace("/", "_")
        return f"dsa:rate_limit:{identifier}:{clean_endpoint}"

    @staticmethod
    def custom(prefix: str, identifier: str) -> str:
        """Format custom namespace cache key."""
        return f"dsa:{prefix}:{identifier}"
