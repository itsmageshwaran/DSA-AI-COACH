"""Unit tests for OpenTelemetry infrastructure and status utilities."""

from __future__ import annotations

from fastapi import FastAPI
import pytest

from src.infrastructure.telemetry.tracer import (
    check_telemetry_status,
    get_current_trace_id,
    init_telemetry,
    shutdown_telemetry,
)


@pytest.mark.anyio
async def test_telemetry_disabled_by_default() -> None:
    """Verify OpenTelemetry status is disabled when OTEL_ENABLED=false."""
    app = FastAPI()
    init_telemetry(app)

    status = check_telemetry_status()
    assert status == "disabled"

    trace_id = get_current_trace_id()
    assert trace_id is None

    shutdown_telemetry()
