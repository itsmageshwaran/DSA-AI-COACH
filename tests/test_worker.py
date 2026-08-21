"""Unit and integration tests for background worker infrastructure."""

from __future__ import annotations

import pytest

from src.infrastructure.worker.queue import check_worker_health, enqueue_job
from src.infrastructure.worker.worker import WorkerSettings, ping_task, sample_background_job


@pytest.mark.anyio
async def test_worker_settings_task_registration() -> None:
    """Verify WorkerSettings registers task functions and timeout configurations."""
    assert ping_task in WorkerSettings.functions
    assert sample_background_job in WorkerSettings.functions
    assert WorkerSettings.job_timeout > 0
    assert WorkerSettings.max_tries > 0


@pytest.mark.anyio
async def test_ping_task_handler() -> None:
    """Verify ping_task handler returns pong response."""
    result = await ping_task({"job_id": "job_123"}, message="healthcheck")
    assert result == "Ping response: healthcheck"


@pytest.mark.anyio
async def test_sample_background_job_handler() -> None:
    """Verify sample_background_job processes payload dict."""
    payload = {"key1": "val1", "key2": 42}
    result = await sample_background_job({"job_id": "job_456"}, "test_task", payload)

    assert result["status"] == "completed"
    assert result["task_name"] == "test_task"
    assert set(result["processed_keys"]) == {"key1", "key2"}


@pytest.mark.anyio
async def test_enqueue_job_and_check_worker_health() -> None:
    """Verify enqueue_job executes without crashing and check_worker_health returns status."""
    job_id = await enqueue_job("ping_task", message="test_enqueue")
    # Returns job_id string when connected to Redis, or None when offline in dev
    assert job_id is None or isinstance(job_id, str)

    status = await check_worker_health()
    assert status in {"running", "disabled", "unavailable"}
