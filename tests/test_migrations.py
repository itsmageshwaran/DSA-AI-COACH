"""Alembic migrations tests."""

from __future__ import annotations

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory


@pytest.mark.anyio
async def test_alembic_configuration_loads() -> None:
    """Verify Alembic configuration file can be loaded and read."""
    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)
    assert script is not None
