"""arq Worker task handlers and execution configuration."""

from __future__ import annotations

from typing import Any

from arq.connections import RedisSettings

from src.core.config.settings import settings
from src.core.logging.logger import logger


async def ping_task(ctx: dict[str, Any], message: str = "pong") -> str:
    """Sample ping background task for testing worker processing."""
    logger.info("Executing background ping_task", message=message, job_id=ctx.get("job_id"))
    return f"Ping response: {message}"


async def sample_background_job(ctx: dict[str, Any], task_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Sample general background job execution handler."""
    logger.info("Executing sample background job", task_name=task_name, payload=payload)
    return {"status": "completed", "task_name": task_name, "processed_keys": list(payload.keys())}


async def startup(ctx: dict[str, Any]) -> None:
    """Worker process startup initialization handler."""
    logger.info("Background worker process initialized and ready for jobs")


async def shutdown(ctx: dict[str, Any]) -> None:
    """Worker process shutdown handler."""
    logger.info("Background worker process shutting down")


class WorkerSettings:
    """arq Worker process configuration class."""

    functions = [ping_task, sample_background_job]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 10
    job_timeout = settings.worker_timeout
    max_tries = settings.worker_max_retries
