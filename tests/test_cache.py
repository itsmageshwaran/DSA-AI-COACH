"""Unit and integration tests for Cache abstraction, serialization, and CacheKey helpers."""

from __future__ import annotations

import pytest

from src.infrastructure.cache import Cache, CacheKey


@pytest.mark.anyio
async def test_cache_key_generation_helpers() -> None:
    """Verify CacheKey helper generates deterministic, namespaced keys."""
    assert CacheKey.session("sess_123") == "dsa:session:sess_123"
    assert CacheKey.prompt_template("socratic", "1") == "dsa:prompt:socratic:v1"
    assert CacheKey.learning_progress("user_99") == "dsa:progress:user_99"
    assert CacheKey.rate_limit("127.0.0.1", "/api/v1/auth/login") == "dsa:rate_limit:127.0.0.1:api_v1_auth_login"
    assert CacheKey.custom("analytics", "metric_1") == "dsa:analytics:metric_1"

    llm_key = CacheKey.llm_response("What is dynamic programming?")
    assert llm_key.startswith("dsa:llm_resp:")


@pytest.mark.anyio
async def test_cache_get_set_delete_exists() -> None:
    """Verify get, set, delete, exists operations on Cache service."""
    cache = Cache()
    test_key = "dsa:test:simple_key"

    # Set value
    success = await cache.set(test_key, "hello_world", ttl=60)
    assert success is True

    # Exists check
    exists = await cache.exists(test_key)
    assert exists is True

    # Get value
    val = await cache.get(test_key)
    assert val == "hello_world"

    # Delete value
    deleted = await cache.delete(test_key)
    assert deleted is True

    # Verify deleted
    val_after = await cache.get(test_key)
    assert val_after is None


@pytest.mark.anyio
async def test_cache_json_serialization() -> None:
    """Verify complex dictionary/list data structures serialize and deserialize correctly."""
    cache = Cache()
    key = "dsa:test:json_data"
    payload = {"user_id": "u123", "scores": [90, 85, 95], "active": True}

    await cache.set(key, payload, ttl=120)
    retrieved = await cache.get(key)

    assert isinstance(retrieved, dict)
    assert retrieved["user_id"] == "u123"
    assert retrieved["scores"] == [90, 85, 95]
    assert retrieved["active"] is True

    await cache.delete(key)


@pytest.mark.anyio
async def test_cache_get_or_set_pattern() -> None:
    """Verify get_or_set executes factory when key is missing and returns cached value on second call."""
    cache = Cache()
    key = "dsa:test:get_or_set_key"
    call_count = 0

    async def db_fetch_factory() -> dict[str, str]:
        nonlocal call_count
        call_count += 1
        return {"data": "from_db"}

    # First call: executes factory
    val1 = await cache.get_or_set(key, db_fetch_factory, ttl=60)
    assert val1 == {"data": "from_db"}
    assert call_count == 1

    # Second call: returns cached value without calling factory
    val2 = await cache.get_or_set(key, db_fetch_factory, ttl=60)
    assert val2 == {"data": "from_db"}
    assert call_count == 1

    await cache.delete(key)


@pytest.mark.anyio
async def test_cache_expire() -> None:
    """Verify expire updates TTL for existing cache entry."""
    cache = Cache()
    key = "dsa:test:expire_key"

    await cache.set(key, "temp_data", ttl=100)
    updated = await cache.expire(key, 200)
    assert updated is True

    await cache.delete(key)
