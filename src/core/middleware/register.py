"""Central registration point for FastAPI middlewares."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.core.config.settings import settings
from src.core.middleware.request_id import RequestIDMiddleware
from src.core.observability.metrics import PrometheusMetricsMiddleware


def register_middlewares(app: FastAPI) -> None:
    """Add middlewares to the FastAPI app in a deterministic order."""
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(GZipMiddleware, minimum_size=500)

    app.add_middleware(RequestIDMiddleware)

    app.add_middleware(PrometheusMetricsMiddleware)
