"""Generic Repository CRUD tests."""

from __future__ import annotations

import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base, BaseModel
from src.infrastructure.database.engine import engine
from src.infrastructure.database.repository import Repository
from src.infrastructure.database.session import AsyncSessionFactory


class SampleItem(BaseModel):
    """Concrete model for testing generic repository."""

    __tablename__ = "sample_items"

    name: Mapped[str] = mapped_column(String(100), nullable=False)


@pytest.fixture(autouse=True)
async def setup_test_tables() -> None:
    """Create test tables before running repository tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.mark.anyio
async def test_repository_crud() -> None:
    """Verify create, get_by_id, list, update, and delete in Repository."""
    async with AsyncSessionFactory() as session:
        repo = Repository(SampleItem, session)

        # 1. Create
        item = SampleItem(name="Test Item 1")
        created = await repo.create(item)
        assert created.id is not None
        assert created.name == "Test Item 1"

        # 2. Get by ID
        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.name == "Test Item 1"

        # 3. List
        items = await repo.list()
        assert len(items) >= 1

        # 4. Update
        updated = await repo.update(fetched, name="Updated Name")
        assert updated.name == "Updated Name"

        # 5. Delete
        await repo.delete(updated)
        deleted = await repo.get_by_id(created.id)
        assert deleted is None
