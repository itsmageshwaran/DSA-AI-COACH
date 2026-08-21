"""Test fixtures used across the test suite.

The ``app`` fixture instantiates a fresh FastAPI application through ``create_app()``
for each test.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.infrastructure.database.models import Base
from src.infrastructure.database.engine import engine
from src.main import create_app
from src.infrastructure.ai.gateway import ai_gateway

@pytest.fixture(autouse=True)
def mock_ai_gateway():
    """Ensure ai_gateway uses mock provider for tests."""
    original_provider = ai_gateway.default_provider_name
    ai_gateway.default_provider_name = "mock"
    yield
    ai_gateway.default_provider_name = original_provider


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio event loop for anyio-compatible test fixtures."""
    return "asyncio"


@pytest.fixture(autouse=True)
async def prepare_database() -> None:
    """Drop and recreate test tables before each test for complete isolation."""
    async with engine.begin() as conn:
        # SQLite can throw OperationalError (database is locked) if tests hold active connections.
        # By ensuring test DBs are isolated or connections are explicitly rolled back, we avoid this.
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def app() -> FastAPI:
    """Instantiate fresh application instance via create_app()."""
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client for the application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    """Provide an authenticated async test client."""
    user_reg = {"email": "test_auth_client@example.com", "password": "Password123"}
    await client.post("/api/v1/auth/register", json=user_reg)
    login_res = await client.post("/api/v1/auth/login", json=user_reg)
    token = login_res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
