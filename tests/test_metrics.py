"""Integration tests for Prometheus metrics endpoint and counters."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient

from src.core.observability.metrics import CACHE_OPERATIONS, QUEUE_OPERATIONS


@pytest.mark.anyio
async def test_metrics_endpoint_returns_prometheus_format(client: AsyncClient) -> None:
    """Verify /metrics returns Prometheus formatted text metrics."""
    response = await client.get("/metrics")
    assert response.status_code == status.HTTP_200_OK
    assert "text/plain" in response.headers.get("content-type", "")
    content = response.text
    assert "dsa_http_requests_total" in content or "python_info" in content


@pytest.mark.anyio
async def test_custom_metric_counters_increment() -> None:
    """Verify CACHE_OPERATIONS and QUEUE_OPERATIONS counters increment without error."""
    CACHE_OPERATIONS.labels(operation="get", status="hit").inc()
    QUEUE_OPERATIONS.labels(operation="enqueue", status="success").inc()
