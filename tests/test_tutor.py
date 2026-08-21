"""Tests for Real-Time Socratic Tutor WebSocket endpoints."""

import json
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.infrastructure.agents.tutor_service import tutor_service
from src.main import create_app


@pytest.fixture
def sync_client() -> Generator[TestClient, None, None]:
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_gateway():
    """Mock the AI Gateway streaming."""
    with patch.object(tutor_service, "gateway") as mock:

        async def mock_generate_stream(*args, **kwargs):
            yield "Hello "
            yield "from "
            yield "mock "
            yield "agent!"

        mock.generate_stream = mock_generate_stream
        yield mock


@pytest.fixture
def auth_token(sync_client):
    """Create a user and return an auth token."""
    user_reg = {"email": "ws_tutor@example.com", "password": "Password123"}
    sync_client.post("/api/v1/auth/register", json=user_reg)
    login_res = sync_client.post("/api/v1/auth/login", json=user_reg)
    return login_res.json()["access_token"]


def test_tutor_websocket_socratic_guide(mock_gateway, auth_token, sync_client) -> None:
    """Test Socratic Guide websocket stream."""
    with sync_client.websocket_connect(f"/api/v1/ws/tutor?token={auth_token}") as websocket:
        websocket.send_text(
            json.dumps(
                {
                    "action": "socratic_guide",
                    "code": "def foo(): pass",
                    "execution_result": {"status": "passed"},
                    "ast_analysis": {"is_safe": True},
                }
            )
        )

        # 1. start event
        data1 = websocket.receive_json()
        assert data1 == {"event": "stream_start", "action": "socratic_guide"}

        # 2-5. token events
        data2 = websocket.receive_json()
        assert data2 == {"event": "token", "chunk": "Hello "}

        data3 = websocket.receive_json()
        assert data3 == {"event": "token", "chunk": "from "}

        data4 = websocket.receive_json()
        assert data4 == {"event": "token", "chunk": "mock "}

        data5 = websocket.receive_json()
        assert data5 == {"event": "token", "chunk": "agent!"}

        # 6. end event
        data6 = websocket.receive_json()
        assert data6 == {"event": "stream_end", "action": "socratic_guide"}


def test_tutor_websocket_invalid_action(mock_gateway, auth_token, sync_client) -> None:
    """Test handling of invalid action."""
    with sync_client.websocket_connect(f"/api/v1/ws/tutor?token={auth_token}") as websocket:
        websocket.send_text(
            json.dumps(
                {
                    "action": "invalid_action",
                    "code": "def foo(): pass",
                }
            )
        )

        data = websocket.receive_json()
        assert data == {"error": "Unknown action: invalid_action"}
