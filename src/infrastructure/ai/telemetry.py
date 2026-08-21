"""AI Gateway Telemetry and Usage Metering."""

from __future__ import annotations

from prometheus_client import Counter, Histogram

from src.core.logging.logger import logger
from src.infrastructure.ai.schemas import LLMResponse
from src.infrastructure.telemetry.tracer import get_current_trace_id

LLM_REQUEST_COUNT = Counter(
    "dsa_llm_requests_total",
    "Total LLM generation requests count",
    ["provider", "model", "status"],
)

LLM_TOKEN_COUNT = Counter(
    "dsa_llm_tokens_total",
    "Total LLM tokens consumed",
    ["provider", "model", "type"],
)

LLM_LATENCY = Histogram(
    "dsa_llm_request_duration_seconds",
    "LLM request duration latency in seconds",
    ["provider", "model"],
)


def record_llm_telemetry(response: LLMResponse) -> None:
    """Record LLM generation telemetry metrics across Prometheus and OpenTelemetry."""
    trace_id = get_current_trace_id()

    # Increment Prometheus metrics
    LLM_REQUEST_COUNT.labels(
        provider=response.provider_name,
        model=response.model_name,
        status="success",
    ).inc()

    LLM_TOKEN_COUNT.labels(
        provider=response.provider_name,
        model=response.model_name,
        type="prompt",
    ).inc(response.prompt_tokens)

    LLM_TOKEN_COUNT.labels(
        provider=response.provider_name,
        model=response.model_name,
        type="completion",
    ).inc(response.completion_tokens)

    LLM_LATENCY.labels(
        provider=response.provider_name,
        model=response.model_name,
    ).observe(response.latency_ms / 1000.0)

    logger.info(
        "LLM Generation Completed: Provider={}, Model={}, Tokens={}, Latency={}ms",
        response.provider_name,
        response.model_name,
        response.total_tokens,
        response.latency_ms,
        trace_id=trace_id,
    )
