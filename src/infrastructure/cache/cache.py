"""Generic async cache abstraction with Redis backend and in-memory fallback."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import json
import time
from typing import Any

from redis.asyncio import Redis, RedisError

from src.core.config.settings import settings
from src.core.logging.logger import logger
from src.infrastructure.redis.connection import get_redis_client


class InMemoryCacheStore:
    """In-memory fallback cache dictionary used when Redis is unavailable."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float | None]] = {}

    def get(self, key: str) -> str | None:
        """Retrieve key value from in-memory fallback store."""
        if key not in self._store:
            return None
        val, expiry = self._store[key]
        if expiry is not None and time.time() > expiry:
            del self._store[key]
            return None
        return val

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Store key value in in-memory fallback store with optional TTL."""
        expiry = time.time() + ttl if ttl is not None else None
        self._store[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        """Delete key from in-memory store."""
        return self._store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        """Check if key exists in in-memory store."""
        return self.get(key) is not None

    def expire(self, key: str, ttl: int) -> bool:
        """Set new TTL for key in in-memory store."""
        if key in self._store:
            val, _ = self._store[key]
            self._store[key] = (val, time.time() + ttl)
            return True
        return False

    def clear(self) -> None:
        """Clear all entries from in-memory store."""
        self._store.clear()


in_memory_fallback = InMemoryCacheStore()


class Cache:
    """Generic async Cache service managing serialization, TTLs, and backend fallback."""

    def __init__(self, client: Redis | None = None) -> None:
        self._override_client = client

    @property
    def _client(self) -> Redis | None:
        if self._override_client is not None:
            return self._override_client
        return get_redis_client()

    async def get(self, key: str) -> Any | None:
        """Retrieve value from cache with automatic JSON deserialization."""
        client = self._client
        if client is not None:
            try:
                raw_val = await client.get(key)
                if raw_val is None:
                    return None
                try:
                    return json.loads(raw_val)
                except (json.JSONDecodeError, TypeError):
                    return raw_val
            except (RedisError, OSError, Exception) as exc:
                logger.warning("Cache get error. Falling back to in-memory store.", key=key, error=str(exc))

        # Fallback to in-memory store
        raw_mem = in_memory_fallback.get(key)
        if raw_mem is None:
            return None
        try:
            return json.loads(raw_mem)
        except (json.JSONDecodeError, TypeError):
            return raw_mem

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """Store value in cache with optional TTL (defaults to settings.cache_default_ttl)."""
        effective_ttl = ttl if ttl is not None else settings.cache_default_ttl
        serialized = json.dumps(value) if isinstance(value, (dict, list, tuple, bool, int, float)) else str(value)

        client = self._client
        if client is not None:
            try:
                if effective_ttl > 0:
                    await client.setex(key, effective_ttl, serialized)
                else:
                    await client.set(key, serialized)
                return True
            except (RedisError, OSError, Exception) as exc:
                logger.warning("Cache set error. Using in-memory fallback.", key=key, error=str(exc))

        # Fallback to in-memory store
        in_memory_fallback.set(key, serialized, effective_ttl if effective_ttl > 0 else None)
        return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        client = self._client
        redis_success = False
        if client is not None:
            try:
                deleted_count = await client.delete(key)
                redis_success = deleted_count > 0
            except (RedisError, OSError, Exception) as exc:
                logger.warning("Cache delete error", key=key, error=str(exc))

        mem_success = in_memory_fallback.delete(key)
        return redis_success or mem_success

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        client = self._client
        if client is not None:
            try:
                count = await client.exists(key)
                if count > 0:
                    return True
            except (RedisError, OSError, Exception) as exc:
                logger.warning("Cache exists error", key=key, error=str(exc))

        return in_memory_fallback.exists(key)

    async def expire(self, key: str, ttl: int) -> bool:
        """Update TTL for an existing cache key."""
        client = self._client
        redis_success = False
        if client is not None:
            try:
                redis_success = bool(await client.expire(key, ttl))
            except (RedisError, OSError, Exception) as exc:
                logger.warning("Cache expire error", key=key, error=str(exc))

        mem_success = in_memory_fallback.expire(key, ttl)
        return redis_success or mem_success

    async def get_or_set(
        self,
        key: str,
        default_factory: Callable[[], Awaitable[Any]],
        ttl: int | None = None,
    ) -> Any:
        """Retrieve key value if present, else execute factory function, cache result and return."""
        cached_val = await self.get(key)
        if cached_val is not None:
            return cached_val

        fresh_val = await default_factory()
        if fresh_val is not None:
            await self.set(key, fresh_val, ttl=ttl)
        return fresh_val


cache = Cache()
