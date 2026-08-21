"""Async background worker queue producer and lifecycle manager using arq."""

from __future__ import annotations

import asyncio
from typing import Any

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from src.core.config.settings import settings
from src.core.logging.logger import logger

_arq_pool: ArqRedis | None = None


async def init_worker() -> None:
    """Initialize arq Redis connection pool for enqueuing background tasks."""
    global _arq_pool  # noqa: PLW0603

    if not settings.worker_enabled:
        logger.info("Background worker service disabled in configuration (WORKER_ENABLED=false)")
        return

    try:
        logger.info("Initializing arq background worker queue connection pool")
        # Parse redis url
        redis_settings = RedisSettings.from_dsn(settings.redis_url)
        _arq_pool = await create_pool(redis_settings)
        logger.info("Background worker pool established successfully")
    except Exception as exc:
        logger.warning(
            "Worker connection initialization failed. Background jobs will execute inline or degrade gracefully.",
            error=str(exc),
        )
        _arq_pool = None


async def close_worker() -> None:
    """Close arq background worker connection pool."""
    global _arq_pool  # noqa: PLW0603

    if _arq_pool is not None:
        logger.info("Closing background worker queue pool")
        try:
            await _arq_pool.close()
        except Exception as exc:
            logger.warning("Error closing worker pool", error=str(exc))
        _arq_pool = None


async def enqueue_job(function_name: str, *args: Any, **kwargs: Any) -> str | None:
    """Enqueue a background task for worker processing.

    If worker pool is offline or WORKER_ENABLED=false, logs execution and returns None.
    """
    if _arq_pool is not None:
        try:
            job = await _arq_pool.enqueue_job(function_name, *args, **kwargs)
            logger.info("Enqueued background job", function=function_name, job_id=job.job_id if job else None)
            return job.job_id if job else None
        except Exception as exc:
            logger.error("Failed to enqueue background job", function=function_name, error=str(exc))
            return None

    logger.info("Inline background job execution (worker pool unavailable)", function=function_name)
    return None


async def check_worker_health() -> str:
    """Check background worker service status.

    Returns:
        "running": Worker enabled and pool connected.
        "disabled": WORKER_ENABLED configuration flag is false.
        "unavailable": Worker enabled but connection pool failed.

    """
    if not settings.worker_enabled:
        return "disabled"

    if _arq_pool is None:
        return "unavailable"

    try:
        ping_ok = await asyncio.wait_for(_arq_pool.ping(), timeout=2.0)
        return "running" if ping_ok else "unavailable"
    except Exception:
        return "unavailable"
