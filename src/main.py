"""Application entry-point."""

from __future__ import annotations

from fastapi import FastAPI, Response

from src.api.v1.router import api_router
from src.core.exceptions.handlers import register_exception_handlers
from src.core.lifespan.events import lifespan
from src.core.middleware.register import register_middlewares
from src.core.observability.metrics import get_metrics_response


def create_app() -> FastAPI:
    """Assemble and configure the FastAPI application."""
    app = FastAPI(
        title="AI-Native Software Engineering Learning Platform",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        description=(
            "A production-ready backend skeleton implementing clean architecture "
            "principles, structured logging and health-check endpoints."
        ),
        lifespan=lifespan,
    )

    # Register global exception handlers
    register_exception_handlers(app)

    # Register middleware (CORS, GZip, TrustedHost, Request-ID, PrometheusMetrics)
    register_middlewares(app)

    # Expose Prometheus /metrics endpoint
    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return get_metrics_response()

    # Include API routers
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
