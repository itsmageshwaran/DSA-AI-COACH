"""Structured logging configuration using loguru."""

from __future__ import annotations

import contextvars
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger as _loguru_logger

from src.core.config.settings import settings

request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


def _patch_record(record: Any) -> None:
    """Inject request_id into record['extra'] from contextvar if not present."""
    if "request_id" not in record["extra"] or record["extra"]["request_id"] is None:
        record["extra"]["request_id"] = request_id_ctx.get()


def _log_format(record: Any) -> str:
    """Convert a Loguru record to a JSON string."""
    req_id = record["extra"].get("request_id")
    req_id_val = f'"{req_id}"' if req_id else "null"
    return (
        f'{{{{"time":"{record["time"].isoformat()}","level":"{record["level"].name}",'
        f'"message":{record["message"]!r},"module":"{record["module"]}",'
        f'"function":"{record["function"]}","line":{record["line"]},'
        f'"request_id":{req_id_val}}}}}\n'
    )


def configure_logging() -> None:
    """Configure Loguru with JSON output and appropriate level."""
    _loguru_logger.remove()
    _loguru_logger.configure(patcher=_patch_record)
    _loguru_logger.add(
        sys.stdout,
        level=settings.log_level,
        format=_log_format,
        backtrace=True,
        diagnose=True,
    )
    if settings.environment == "development":
        log_path = Path(settings.project_root) / "logs" / f"{datetime.now(timezone.utc):%Y-%m-%d}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        _loguru_logger.add(
            str(log_path),
            level="DEBUG",
            format=_log_format,
            backtrace=True,
            diagnose=True,
        )


logger = _loguru_logger
