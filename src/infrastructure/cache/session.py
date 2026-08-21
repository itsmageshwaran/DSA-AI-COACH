"""Redis-backed session store abstraction for temporary workflow, rate-limit, and tutor state."""

from __future__ import annotations

from typing import Any

from src.core.config.settings import settings
from src.infrastructure.cache.cache import Cache, cache
from src.infrastructure.cache.keys import CacheKey


class SessionStore:
    """Session management store utilizing namespaced cache keys and TTL management."""

    def __init__(self, cache_service: Cache | None = None) -> None:
        self._cache = cache_service or cache

    async def create_session(
        self,
        session_id: str,
        data: dict[str, Any],
        ttl: int | None = None,
    ) -> str:
        """Create a new session record with namespaced key and TTL."""
        key = CacheKey.session(session_id)
        effective_ttl = ttl if ttl is not None else settings.session_ttl
        await self._cache.set(key, data, ttl=effective_ttl)
        return session_id

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data by session ID."""
        key = CacheKey.session(session_id)
        val = await self._cache.get(key)
        if isinstance(val, dict):
            return val
        return None

    async def update_session(
        self,
        session_id: str,
        data: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        """Update existing session data and optionally refresh TTL."""
        key = CacheKey.session(session_id)
        existing = await self.get_session(session_id)
        if existing is None:
            return False

        updated_data = {**existing, **data}
        effective_ttl = ttl if ttl is not None else settings.session_ttl
        return await self._cache.set(key, updated_data, ttl=effective_ttl)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session record from store."""
        key = CacheKey.session(session_id)
        return await self._cache.delete(key)

    async def refresh_session_ttl(
        self,
        session_id: str,
        ttl: int | None = None,
    ) -> bool:
        """Refresh expiration TTL for an active session."""
        key = CacheKey.session(session_id)
        effective_ttl = ttl if ttl is not None else settings.session_ttl
        return await self._cache.expire(key, effective_ttl)


session_store = SessionStore()
