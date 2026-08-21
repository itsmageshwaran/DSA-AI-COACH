"""Integration tests for extended health, liveness, and readiness endpoints."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_extended_health_endpoint_returns_all_infrastructure_statuses(client: AsyncClient) -> None:
    """Verify /api/v1/health returns status for database, redis, worker, and telemetry."""
    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "status" in data
    assert data["status"] in {"ok", "degraded", "unavailable"}
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    assert "uptime" in data
    assert "database" in data
    assert data["database"] in {"connected", "unavailable"}
    assert "redis" in data
    assert data["redis"] in {"connected", "disabled", "unavailable"}
    assert "worker" in data
    assert data["worker"] in {"running", "disabled", "unavailable"}
    assert "telemetry" in data
    assert data["telemetry"] in {"enabled", "disabled"}


@pytest.mark.anyio
async def test_liveness_endpoint_returns_alive(client: AsyncClient) -> None:
    """Verify /api/v1/health/live returns HTTP 200 with alive status."""
    response = await client.get("/api/v1/health/live")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.anyio
async def test_readiness_endpoint_structure(client: AsyncClient) -> None:
    """Verify /api/v1/health/ready returns status and services readiness map."""
    response = await client.get("/api/v1/health/ready")
    assert response.status_code in {status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE}

    data = response.json()
    assert "status" in data
    assert data["status"] in {"ready", "not_ready"}
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]
