"""Database connection and engine tests."""

from __future__ import annotations

import pytest
from sqlalchemy import text

from src.infrastructure.database.engine import engine
from src.infrastructure.database.session import AsyncSessionFactory


@pytest.mark.anyio
async def test_database_connection() -> None:
    """Verify raw database connection using async engine."""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.anyio
async def test_async_session_factory() -> None:
    """Verify async session creation and query execution."""
    async with AsyncSessionFactory() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
