"""Async Redis connection manager and health check utilities."""

from __future__ import annotations

import asyncio
from redis.asyncio import ConnectionPool, Redis, RedisError

from src.core.config.settings import settings
from src.core.logging.logger import logger


class RedisClientManager:
    """Singleton manager for async Redis connection pool and client lifecycle."""

    _instance: RedisClientManager | None = None
    _pool: ConnectionPool | None = None
    _client: Redis | None = None

    @classmethod
    def get_instance(cls) -> RedisClientManager:
        """Get or create singleton manager instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """Initialize Redis connection pool and test connectivity."""
        if self._client is not None:
            return

        try:
            logger.info("Initializing Redis connection pool", url=settings.redis_url)
            self._pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                socket_timeout=settings.redis_connect_timeout,
                socket_connect_timeout=settings.redis_connect_timeout,
                decode_responses=True,
            )
            self._client = Redis(connection_pool=self._pool)
            # Test connectivity with ping
            await asyncio.wait_for(self._client.ping(), timeout=settings.redis_connect_timeout)
            logger.info("Redis connection established successfully")
        except Exception as exc:
            logger.warning(
                "Redis connection failed. System operating in degraded mode without cache/queues.",
                error=str(exc),
            )
            # Keep client reference if pool created, but handle operational failure gracefully
            if self._client is None and self._pool is not None:
                self._client = Redis(connection_pool=self._pool)

    async def close(self) -> None:
        """Gracefully close Redis connections and release pool resources."""
        if self._client is not None:
            logger.info("Closing Redis client connections")
            try:
                await self._client.aclose()
            except Exception as exc:
                logger.warning("Error closing Redis client", error=str(exc))
            self._client = None

        if self._pool is not None:
            try:
                await self._pool.disconnect()
            except Exception as exc:
                logger.warning("Error disconnecting Redis pool", error=str(exc))
            self._pool = None

    def get_client(self) -> Redis | None:
        """Return initialized async Redis client instance or None."""
        return self._client


redis_manager = RedisClientManager.get_instance()


async def init_redis() -> None:
    """Lifespan hook to initialize Redis client."""
    await redis_manager.initialize()


async def close_redis() -> None:
    """Lifespan hook to close Redis connections."""
    await redis_manager.close()


def get_redis_client() -> Redis | None:
    """Dependency helper to retrieve current Redis client."""
    return redis_manager.get_client()


async def check_redis_health() -> str:
    """Check Redis health and return connection status string.

    Returns:
        "connected": Redis is online and responding to ping.
        "unavailable": Redis connection failed or ping timed out.

    """
    client = get_redis_client()
    if client is None:
        return "unavailable"

    try:
        ping_ok = await asyncio.wait_for(client.ping(), timeout=2.0)
        return "connected" if ping_ok else "unavailable"
    except (RedisError, OSError, asyncio.TimeoutError, Exception):
        return "unavailable"
