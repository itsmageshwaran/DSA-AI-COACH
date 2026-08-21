"""User repository for async database queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.auth.models import User
from src.infrastructure.database.repository import Repository


class UserRepository(Repository[User]):
    """Async repository for User domain model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by email address including role relationship."""
        result = await self.session.execute(
            select(User).options(joinedload(User.role), joinedload(User.profile)).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_role(self, user_id: str) -> User | None:
        """Fetch user by ID with role loaded."""
        result = await self.session.execute(
            select(User).options(joinedload(User.role), joinedload(User.profile)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
