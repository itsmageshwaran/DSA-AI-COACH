"""Role repository for async database queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import Role
from src.infrastructure.database.repository import Repository


class RoleRepository(Repository[Role]):
    """Async repository for Role domain model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Role, session)

    async def get_by_name(self, name: str) -> Role | None:
        """Fetch role by name."""
        result = await self.session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()
