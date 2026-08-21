import pytest
from httpx import AsyncClient

from src.infrastructure.database.base import Base
from src.infrastructure.database.engine import engine
from src.domain.learning.models import Concept


@pytest.fixture(autouse=True)
async def prepare_database() -> None:
    """Drop and recreate tables before each API test."""
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            pass
        await conn.run_sync(Base.metadata.create_all)


async def get_user_headers(client: AsyncClient, email: str = "test@example.com") -> dict[str, str]:
    user_reg = {"email": email, "password": "Password123"}
    await client.post("/api/v1/auth/register", json=user_reg)
    login_user = await client.post("/api/v1/auth/login", json=user_reg)
    user_token = login_user.json()["access_token"]
    return {"Authorization": f"Bearer {user_token}"}


@pytest.mark.anyio
async def test_record_concept_review(client: AsyncClient) -> None:
    headers = await get_user_headers(client)

    # We need a valid concept in the database to review. We'll use the API if possible,
    # but creating a concept requires admin role. Let's just create an admin user and create a concept.
    admin_reg = {"email": "admin@example.com", "password": "Password123"}
    await client.post("/api/v1/auth/register", json=admin_reg)

    # We can bypass API creation and directly use sqlalchemy if we add db_session fixture,
    # but anyio and AsyncClient is simpler if we just use a db_session here.
    # However, db_session fixture is not available. Let's create an async session manager locally.
    # Actually, we can get an async session directly from the factory.
    from src.infrastructure.database.session import AsyncSessionFactory

    async with AsyncSessionFactory() as session:
        concept = Concept(name="Review Test Concept")
        session.add(concept)
        await session.commit()
        await session.refresh(concept)
        concept_id = concept.id

    response = await client.post(
        f"/api/v1/learning-intelligence/concepts/{concept_id}/review", json={"grade": 4}, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["concept_id"] == concept_id
    assert "next_review_date" in data

    response2 = await client.post(
        f"/api/v1/learning-intelligence/concepts/{concept_id}/review", json={"grade": 5}, headers=headers
    )
    assert response2.status_code == 200


@pytest.mark.anyio
async def test_get_due_reviews(client: AsyncClient) -> None:
    headers = await get_user_headers(client, "due@example.com")
    response = await client.get("/api/v1/learning-intelligence/reviews/due", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_recommendations(client: AsyncClient) -> None:
    headers = await get_user_headers(client, "rec@example.com")
    response = await client.get("/api/v1/learning-intelligence/recommendations", headers=headers)
    assert response.status_code == 200
    assert "due_concept_ids" in response.json()
