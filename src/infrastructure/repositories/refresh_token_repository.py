"""RefreshToken repository for async database queries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import RefreshToken
from src.infrastructure.database.repository import Repository


class RefreshTokenRepository(Repository[RefreshToken]):
    """Async repository for RefreshToken domain model."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshToken, session)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Fetch refresh token record by token string."""
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.token == token))
        return result.scalar_one_or_none()

    async def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token."""
        record = await self.get_by_token(token)
        if record and not record.is_revoked:
            record.is_revoked = True
            await self.session.flush()
            return True
        return False
