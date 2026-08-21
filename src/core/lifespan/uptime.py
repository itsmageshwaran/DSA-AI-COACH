"""Utility to calculate application uptime."""

from __future__ import annotations

import time

_start_time: float = time.time()


def set_start_time() -> None:
    """Record application start timestamp."""
    global _start_time
    _start_time = time.time()


def get_uptime() -> float:
    """Return elapsed seconds since startup."""
    return round(time.time() - _start_time, 4)
