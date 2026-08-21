"""Auth module unit and integration tests."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_user_success(client: AsyncClient) -> None:
    """Verify user registration with valid credentials."""
    payload = {
        "email": "user@example.com",
        "password": "Password123",
        "full_name": "Test User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["full_name"] == "Test User"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.anyio
async def test_register_user_duplicate_email(client: AsyncClient) -> None:
    """Registering duplicate email should return HTTP 400."""
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123",
    }
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED

    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_login_success_and_invalid_password(client: AsyncClient) -> None:
    """Verify login with correct credentials and rejection on invalid password."""
    # 1. Register
    reg_payload = {"email": "login@example.com", "password": "SecretPassword1"}
    await client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Login invalid password
    invalid_login = {"email": "login@example.com", "password": "WrongPassword1"}
    res_bad = await client.post("/api/v1/auth/login", json=invalid_login)
    assert res_bad.status_code == status.HTTP_401_UNAUTHORIZED

    # 3. Login valid password
    valid_login = {"email": "login@example.com", "password": "SecretPassword1"}
    res_good = await client.post("/api/v1/auth/login", json=valid_login)
    assert res_good.status_code == status.HTTP_200_OK
    tokens = res_good.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.anyio
async def test_refresh_token_flow_and_logout(client: AsyncClient) -> None:
    """Verify refresh token flow and revocation on logout."""
    reg_payload = {"email": "refresh@example.com", "password": "SecretPassword1"}
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json=reg_payload)
    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    # Refresh
    ref_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_res.status_code == status.HTTP_200_OK
    new_tokens = ref_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    # Logout
    logout_res = await client.post("/api/v1/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
    assert logout_res.status_code == status.HTTP_200_OK

    # Re-using revoked refresh token should fail
    ref_revoked = await client.post("/api/v1/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]})
    assert ref_revoked.status_code == status.HTTP_401_UNAUTHORIZED
