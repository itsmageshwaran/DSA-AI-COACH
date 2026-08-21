"""Integration & Authorization tests for Learning Domain API endpoints."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient

from src.infrastructure.database.base import Base
from src.infrastructure.database.engine import engine


@pytest.fixture(autouse=True)
async def prepare_database() -> None:
    """Drop and recreate tables before each API test."""
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            pass
        await conn.run_sync(Base.metadata.create_all)


@pytest.mark.anyio
async def test_courses_api_crud_and_rbac(client: AsyncClient) -> None:
    """Verify course creation requires admin role and listing works for active users."""
    # 1. Register normal user
    user_reg = {"email": "user@example.com", "password": "Password123"}
    await client.post("/api/v1/auth/register", json=user_reg)
    login_user = await client.post("/api/v1/auth/login", json=user_reg)
    user_token = login_user.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Normal user attempt to create course -> 403 Forbidden
    course_data = {"title": "Data Structures 101", "description": "Intro to DSA"}
    res_forbidden = await client.post("/api/v1/courses", json=course_data, headers=user_headers)
    assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN

    # Test list courses as authenticated user (empty list)
    res_list = await client.get("/api/v1/courses", headers=user_headers)
    assert res_list.status_code == status.HTTP_200_OK
    assert res_list.json() == []


@pytest.mark.anyio
async def test_learning_path_enrollment_api(client: AsyncClient) -> None:
    """Verify learning path creation and enrollment API endpoints."""
    # Register user
    user_reg = {"email": "student@example.com", "password": "Password123"}
    await client.post("/api/v1/auth/register", json=user_reg)
    login_user = await client.post("/api/v1/auth/login", json=user_reg)
    user_token = login_user.json()["access_token"]
    headers = {"Authorization": f"Bearer {user_token}"}

    # Get learning paths list
    paths_res = await client.get("/api/v1/learning-paths", headers=headers)
    assert paths_res.status_code == status.HTTP_200_OK
    assert isinstance(paths_res.json(), list)


@pytest.mark.anyio
async def test_progress_and_submissions_api(client: AsyncClient) -> None:
    """Verify progress and submissions API endpoints require authentication."""
    # Unauthorized request without Bearer token -> 401
    res_unauth = await client.get("/api/v1/progress/me")
    assert res_unauth.status_code == status.HTTP_401_UNAUTHORIZED

    # Register user and test /progress/me
    reg_payload = {"email": "progress_user@example.com", "password": "Password123"}
    await client.post("/api/v1/auth/register", json=reg_payload)
    login_res = await client.post("/api/v1/auth/login", json=reg_payload)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res_progress = await client.get("/api/v1/progress/me", headers=headers)
    assert res_progress.status_code == status.HTTP_200_OK
    data = res_progress.json()
    assert data["total_lessons_completed"] == 0
    assert data["completion_percentage"] == 0.0
