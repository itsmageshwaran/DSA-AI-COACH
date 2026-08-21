"""Prometheus-compatible metrics collection and middleware instrumentation."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config.settings import settings

if TYPE_CHECKING:
    from fastapi import Request

# Prometheus Metric Counters and Histograms
REQUEST_COUNT = Counter(
    "dsa_http_requests_total",
    "Total HTTP request count",
    ["method", "handler", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "dsa_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "handler"],
)

CACHE_OPERATIONS = Counter(
    "dsa_cache_operations_total",
    "Total cache operations count",
    ["operation", "status"],
)

QUEUE_OPERATIONS = Counter(
    "dsa_queue_operations_total",
    "Total background queue operations count",
    ["operation", "status"],
)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking HTTP request rates, response codes, and latency metrics."""

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        """Record HTTP metrics if METRICS_ENABLED is true."""
        if not settings.metrics_enabled or request.url.path in {"/metrics", "/health", "/api/v1/health"}:
            return await call_next(request)  # type: ignore[no-any-return]

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        duration = time.perf_counter() - start_time

        handler = request.scope.get("path", "unknown")
        method = request.method
        status_code = str(response.status_code)

        REQUEST_COUNT.labels(method=method, handler=handler, status_code=status_code).inc()
        REQUEST_LATENCY.labels(method=method, handler=handler).observe(duration)

        return response


def get_metrics_response() -> Response:
    """Generate Prometheus formatted text response for /metrics route."""
    if not settings.metrics_enabled:
        return Response("Metrics collection disabled", status_code=404, media_type="text/plain")

    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
