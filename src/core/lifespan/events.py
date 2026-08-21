"""Modern FastAPI lifespan context manager for application startup and shutdown."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.core.config.settings import settings
from src.core.lifespan.uptime import set_start_time
from src.core.logging.logger import configure_logging, logger
from src.infrastructure.redis.connection import close_redis, init_redis
from src.infrastructure.telemetry.tracer import init_telemetry, shutdown_telemetry
from src.infrastructure.worker.queue import close_worker, init_worker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Execute startup and shutdown infrastructure logic around request handling."""
    # Startup
    set_start_time()
    configure_logging()
    logger.info(
        "Application startup",
        environment=settings.environment,
        app_name=settings.app_name,
    )

    # Initialize Telemetry, Redis, and Worker Infrastructure
    init_telemetry(app)
    await init_redis()
    await init_worker()

    yield

    # Shutdown Infrastructure Components
    logger.info("Application shutdown initiating")
    await close_worker()
    await close_redis()
    shutdown_telemetry()
    logger.info("Application shutdown complete")
