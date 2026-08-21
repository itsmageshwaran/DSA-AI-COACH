"""Unit of Work transaction management tests."""

from __future__ import annotations

import pytest

from tests.test_repository import SampleItem
from src.infrastructure.database.repository import Repository
from src.infrastructure.database.unit_of_work import UnitOfWork


@pytest.mark.anyio
async def test_unit_of_work_commit() -> None:
    """Verify changes are committed when uow.commit() is called."""
    async with UnitOfWork() as uow:
        repo = Repository(SampleItem, uow.session)
        item = SampleItem(name="UOW Commit Item")
        created = await repo.create(item)
        item_id = created.id
        await uow.commit()

    async with UnitOfWork() as uow:
        repo = Repository(SampleItem, uow.session)
        fetched = await repo.get_by_id(item_id)
        assert fetched is not None
        assert fetched.name == "UOW Commit Item"


@pytest.mark.anyio
async def test_unit_of_work_rollback_on_exception() -> None:
    """Verify changes are rolled back automatically when an exception is raised."""
    item_id: str | None = None
    try:
        async with UnitOfWork() as uow:
            repo = Repository(SampleItem, uow.session)
            item = SampleItem(name="UOW Rollback Item")
            created = await repo.create(item)
            item_id = created.id
            msg = "Trigger transaction rollback"
            raise RuntimeError(msg)
    except RuntimeError:
        pass

    assert item_id is not None
    async with UnitOfWork() as uow:
        repo = Repository(SampleItem, uow.session)
        fetched = await repo.get_by_id(item_id)
        assert fetched is None
