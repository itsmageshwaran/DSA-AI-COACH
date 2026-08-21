"""Unit and integration tests for Redis connection manager and health check."""

from __future__ import annotations

import pytest

from src.infrastructure.redis.connection import (
    RedisClientManager,
    check_redis_health,
    get_redis_client,
)


@pytest.mark.anyio
async def test_redis_client_manager_singleton() -> None:
    """Verify RedisClientManager follows singleton pattern."""
    m1 = RedisClientManager.get_instance()
    m2 = RedisClientManager.get_instance()
    assert m1 is m2


@pytest.mark.anyio
async def test_check_redis_health_status() -> None:
    """Verify check_redis_health returns string status without raising errors."""
    health_status = await check_redis_health()
    assert health_status in {"connected", "unavailable"}


@pytest.mark.anyio
async def test_get_redis_client_helper() -> None:
    """Verify get_redis_client returns Redis instance or None when offline."""
    client = get_redis_client()
    # May be None in test environment if local Redis server is offline
    if client is not None:
        assert hasattr(client, "ping")
