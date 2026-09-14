"""SQLAlchemy 2.0 Async Engine configuration."""

from __future__ import annotations

from typing import Any
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.core.config.settings import settings


def get_engine_kwargs(url: str) -> dict[str, Any]:
    """Build kwargs for create_async_engine based on dialect."""
    from sqlalchemy.pool import StaticPool

    kwargs: dict[str, Any] = {
        "echo": settings.database_echo,
        "future": True,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    if "sqlite" not in url:
        kwargs["pool_size"] = settings.pool_size
        kwargs["max_overflow"] = settings.max_overflow
        kwargs["pool_timeout"] = 30
        if "postgresql" in url or "asyncpg" in url:
            kwargs["connect_args"] = {
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "server_settings": {"jit": "off"},
            }
    else:
        kwargs["poolclass"] = StaticPool
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    **get_engine_kwargs(settings.database_url),
)
