"""Unit and integration tests for SessionStore."""

from __future__ import annotations

import pytest

from src.infrastructure.cache.session import SessionStore


@pytest.mark.anyio
async def test_session_create_get_update_delete() -> None:
    """Test full CRUD lifecycle of SessionStore."""
    store = SessionStore()
    session_id = "test_sess_001"
    initial_data = {"user_id": "u123", "role": "learner", "step": 1}

    # 1. Create session
    created_id = await store.create_session(session_id, initial_data, ttl=300)
    assert created_id == session_id

    # 2. Get session
    retrieved = await store.get_session(session_id)
    assert retrieved is not None
    assert retrieved["user_id"] == "u123"
    assert retrieved["step"] == 1

    # 3. Update session
    updated = await store.update_session(session_id, {"step": 2, "completed": True}, ttl=300)
    assert updated is True

    # 4. Verify update
    after_update = await store.get_session(session_id)
    assert after_update is not None
    assert after_update["step"] == 2
    assert after_update["completed"] is True

    # 5. Refresh TTL
    refreshed = await store.refresh_session_ttl(session_id, ttl=600)
    assert refreshed is True

    # 6. Delete session
    deleted = await store.delete_session(session_id)
    assert deleted is True

    # 7. Verify deletion
    after_delete = await store.get_session(session_id)
    assert after_delete is None


@pytest.mark.anyio
async def test_update_non_existent_session_returns_false() -> None:
    """Updating non-existent session should return False."""
    store = SessionStore()
    result = await store.update_session("non_existent_sess", {"key": "val"})
    assert result is False
