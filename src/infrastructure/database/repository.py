"""Generic Repository pattern implementation for Async CRUD operations."""

from __future__ import annotations

from typing import Any, Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class Repository(Generic[T]):
    """Generic async repository providing CRUD operations."""

    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: str) -> T | None:
        """Fetch entity by primary key ID."""
        result = await self.session.execute(select(self.model).where(self.model.id == entity_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[T]:
        """Fetch all entities without pagination limit."""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        """List entities with pagination."""
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        """Add new entity to session."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T, **kwargs: Any) -> T:
        """Update entity fields."""
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """Delete entity from session."""
        await self.session.delete(entity)
        await self.session.flush()
