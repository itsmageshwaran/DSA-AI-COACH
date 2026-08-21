"""OpenTelemetry foundation for distributed tracing and observability."""

from __future__ import annotations

from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.core.config.settings import settings
from src.core.logging.logger import logger

if TYPE_CHECKING:
    from fastapi import FastAPI

_tracer_provider: TracerProvider | None = None


def init_telemetry(app: FastAPI) -> None:
    """Initialize OpenTelemetry tracer provider, OTLP exporter, and FastAPI auto-instrumentation."""
    global _tracer_provider  # noqa: PLW0603

    if not settings.otel_enabled:
        logger.info("OpenTelemetry tracing disabled in configuration (OTEL_ENABLED=false)")
        return

    try:
        logger.info(
            "Initializing OpenTelemetry provider",
            service_name=settings.otel_service_name,
            endpoint=settings.otel_exporter_otlp_endpoint,
        )
        resource = Resource.create({SERVICE_NAME: settings.otel_service_name})
        _tracer_provider = TracerProvider(resource=resource)

        if settings.otel_exporter_otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(
                endpoint=settings.otel_exporter_otlp_endpoint,
                insecure=True,
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
            _tracer_provider.add_span_processor(span_processor)

        trace.set_tracer_provider(_tracer_provider)

        # Instrument FastAPI app
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app, tracer_provider=_tracer_provider)
            logger.info("FastAPI OpenTelemetry instrumentation attached successfully")
        except ImportError:
            logger.warning(
                "opentelemetry-instrumentation-fastapi package not installed. Skipping auto-instrumentation."
            )

    except Exception as exc:
        logger.warning("Failed to initialize OpenTelemetry tracing", error=str(exc))
        _tracer_provider = None


def shutdown_telemetry() -> None:
    """Shutdown OpenTelemetry provider and flush remaining spans."""
    global _tracer_provider  # noqa: PLW0603

    if _tracer_provider is not None:
        logger.info("Flushing and shutting down OpenTelemetry tracer provider")
        try:
            _tracer_provider.shutdown()
        except Exception as exc:
            logger.warning("Error shutting down telemetry provider", error=str(exc))
        _tracer_provider = None


def get_current_trace_id() -> str | None:
    """Extract current active OpenTelemetry span trace ID formatted as a hex string."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return f"{span.get_span_context().trace_id:032x}"
    return None


def check_telemetry_status() -> str:
    """Check telemetry status string ("enabled" or "disabled")."""
    return "enabled" if settings.otel_enabled and _tracer_provider is not None else "disabled"
