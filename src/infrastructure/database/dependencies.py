"""FastAPI Dependency Injection providers for database infrastructure."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.infrastructure.database.engine import engine
from src.infrastructure.database.session import AsyncSessionFactory
from src.infrastructure.database.unit_of_work import UnitOfWork


def get_db_engine() -> AsyncEngine:
    """Provide database engine instance."""
    return engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide async database session dependency."""
    async with AsyncSessionFactory() as session:
        yield session


async def get_unit_of_work(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[UnitOfWork, None]:
    """Provide UnitOfWork dependency using injected session."""
    uow = UnitOfWork(session=session)
    async with uow:
        yield uow
