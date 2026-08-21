"""Health check endpoint tests."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_endpoint_returns_200(client: AsyncClient) -> None:
    """The /api/v1/health endpoint must respond with HTTP 200 and complete health metrics."""
    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK

    json_body = response.json()
    assert json_body["status"] == "ok"
    assert json_body["version"] == "0.1.0"
    assert "environment" in json_body
    assert "timestamp" in json_body
    assert "uptime" in json_body
    assert isinstance(json_body["uptime"], (int, float))


@pytest.mark.anyio
async def test_health_endpoint_returns_request_id_header(client: AsyncClient) -> None:
    """Requests should include X-Request-ID header in response."""
    response = await client.get("/api/v1/health")
    assert "x-request-id" in response.headers


@pytest.mark.anyio
async def test_swagger_is_accessible(client: AsyncClient) -> None:
    """OpenAPI documentation should be reachable at /docs."""
    response = await client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "Swagger UI" in response.text
