"""Users module and authorization tests."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_me_unauthorized_without_token(client: AsyncClient) -> None:
    """Accessing /users/me without Bearer token should fail with HTTP 401."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_get_me_invalid_token(client: AsyncClient) -> None:
    """Accessing /users/me with an invalid token should fail with HTTP 401."""
    headers = {"Authorization": "Bearer invalid_token_12345"}
    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_get_me_success(client: AsyncClient) -> None:
    """Accessing /users/me with a valid token returns profile data."""
    reg_payload = {"email": "me@example.com", "password": "Password123", "full_name": "My Profile"}
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json=reg_payload)
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == status.HTTP_200_OK
    data = me_res.json()
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "My Profile"
