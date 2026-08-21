"""Health, liveness, and readiness check endpoints providing service status and infrastructure metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from src.core.config.settings import settings
from src.core.lifespan.uptime import get_uptime
from src.infrastructure.database.engine import engine
from src.infrastructure.redis.connection import check_redis_health
from src.infrastructure.telemetry.tracer import check_telemetry_status
from src.infrastructure.worker.queue import check_worker_health

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema containing service status and infrastructure metrics."""

    status: str
    version: str
    environment: str
    timestamp: datetime
    uptime: float
    database: str
    redis: str
    worker: str
    telemetry: str


class LivenessResponse(BaseModel):
    """Liveness probe response schema."""

    status: str


class ReadinessResponse(BaseModel):
    """Readiness probe response schema."""

    status: str
    services: dict[str, str]


async def check_database_connection() -> str:
    """Check if database connection is alive."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "connected"
    except Exception:
        return "unavailable"


@router.get(
    "/health",
    name="health-check",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
    tags=["Health"],
)
async def health(request: Request) -> HealthResponse:
    """Return comprehensive health status across database, Redis, worker, and telemetry."""
    app_version = getattr(request.app, "version", "0.1.0")

    db_status = await check_database_connection()
    redis_status = await check_redis_health()
    worker_status = await check_worker_health()
    telemetry_status = check_telemetry_status()

    # Determine system overall status
    overall_status = "ok"
    if db_status != "connected" or (redis_status == "unavailable" and settings.environment == "production"):
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        version=app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
        uptime=get_uptime(),
        database=db_status,
        redis=redis_status,
        worker=worker_status,
        telemetry=telemetry_status,
    )


@router.get(
    "/health/live",
    name="health-liveness-check",
    status_code=status.HTTP_200_OK,
    response_model=LivenessResponse,
    tags=["Health"],
)
async def liveness() -> LivenessResponse:
    """Liveness probe confirming application process is running."""
    return LivenessResponse(status="alive")


@router.get(
    "/health/ready",
    name="health-readiness-check",
    response_model=ReadinessResponse,
    tags=["Health"],
)
async def readiness(response: Response) -> ReadinessResponse:
    """Readiness probe verifying required database and Redis connectivity."""
    db_conn = await check_database_connection()
    redis_conn = await check_redis_health()

    db_healthy = db_conn == "connected"
    redis_healthy = redis_conn in {"connected", "disabled"}

    is_ready = db_healthy and redis_healthy

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if is_ready else "not_ready",
        services={
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
        },
    )
