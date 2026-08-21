"""Health check endpoint database integration tests."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_endpoint_detects_database(client: AsyncClient) -> None:
    """The /api/v1/health endpoint must report database: 'connected'."""
    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK

    json_body = response.json()
    assert json_body["status"] == "ok"
    assert "database" in json_body
    assert json_body["database"] == "connected"
