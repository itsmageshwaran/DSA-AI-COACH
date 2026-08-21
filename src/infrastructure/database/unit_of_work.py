"""Unit of Work pattern for transaction management."""

from __future__ import annotations

from typing import Any, Self
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import AsyncSessionFactory


class UnitOfWork:
    """Async Unit of Work for managing database transactions."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session_factory = AsyncSessionFactory
        self.session: AsyncSession = session if session is not None else AsyncSessionFactory()
        self._owns_session = session is None

    async def __aenter__(self) -> Self:
        """Enter context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Exit context manager, performing rollback if an exception occurred."""
        if exc_type is not None:
            await self.rollback()
        if self._owns_session:
            await self.session.close()

    async def commit(self) -> None:
        """Commit current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback current transaction."""
        await self.session.rollback()
