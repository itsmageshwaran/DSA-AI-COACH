"""WebSocket Router for Real-Time Socratic Tutoring."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from src.infrastructure.agents.tutor_service import tutor_service

router = APIRouter()


class TutorConnectionManager:
    """Manages active WebSocket connections for the tutor."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new websocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected websocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def process_message(self, websocket: WebSocket, data: dict[str, Any], context: dict[str, Any] | None = None) -> None:
        """Process incoming client messages and stream agent responses."""
        action = data.get("action")
        code = data.get("code", "")
        execution_result = data.get("execution_result")
        ast_analysis = data.get("ast_analysis")

        if not action:
            await websocket.send_json({"error": "Missing 'action' in payload."})
            return

        if not code or not code.strip():
            code = "# No implementation written yet. Student is requesting starting guidance."

        try:
            if action == "socratic_guide":
                generator = tutor_service.socratic_guide_stream(
                    code=code,
                    execution_result=execution_result,
                    ast_analysis=ast_analysis,
                    context=context,
                )
            elif action == "code_auditor":
                generator = tutor_service.code_auditor_stream(
                    code=code,
                    ast_analysis=ast_analysis,
                    context=context,
                )
            elif action == "complexity_analyst":
                generator = tutor_service.complexity_analyst_stream(code=code, context=context)
            else:
                await websocket.send_json({"error": f"Unknown action: {action}"})
                return

            # Signal start of stream
            await websocket.send_json({"event": "stream_start", "action": action})

            async for chunk in generator:
                await websocket.send_json({"event": "token", "chunk": chunk})

            # Signal end of stream
            await websocket.send_json({"event": "stream_end", "action": action})

        except Exception as e:
            logger.error(f"Error streaming tutor response: {e}")
            await websocket.send_json({"error": str(e)})


manager = TutorConnectionManager()


from src.core.security.jwt import decode_token
from src.infrastructure.database.session import AsyncSessionFactory
from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.database.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.billing.entitlement_service import EntitlementService
from src.domain.auth.models import User


async def get_ws_user(token: str, session: AsyncSession) -> User | None:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        repo = UserRepository(session)
        return await repo.get_by_id_with_role(user_id)
    except Exception:
        return None


@router.websocket("")
async def websocket_tutor_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time multi-agent coaching."""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    async with AsyncSessionFactory() as session:
        user = await get_ws_user(token, session)
        if not user or not user.is_active:
            with open("ws_debug.log", "a") as f:
                f.write(f"Rejected: user={user}, is_active={getattr(user, 'is_active', None)}\n")
            await websocket.close(code=1008, reason="Unauthorized")
            return

        await manager.connect(websocket)
        with open("ws_debug.log", "a") as f:
            f.write(f"Accepted: user={user.id}\n")
        try:
            while True:
                text_data = await websocket.receive_text()
                try:
                    data = json.loads(text_data)

                    # Quota Check
                    uow = UnitOfWork(session=session)
                    entitlement_service = EntitlementService(uow)
                    try:
                        await entitlement_service.consume_quota(
                            user_id=user.id,
                            resource="tutor_messages",
                            amount=1,
                            metadata_info={"action": data.get("action")},
                        )
                    except Exception as e:
                        await websocket.send_json({"error": str(e)})
                        continue

                    # Build context
                    user_context = {
                        "career_goal": user.profile.career_goal if getattr(user, 'profile', None) else "General Software Engineering",
                        "experience_level": user.profile.experience_level if getattr(user, 'profile', None) else "Beginner",
                        "preferred_language": user.profile.preferred_language if getattr(user, 'profile', None) else "python",
                        "exercise_difficulty": data.get("difficulty", "N/A"),
                        "current_concept": data.get("concept", "N/A")
                    }

                    await manager.process_message(websocket, data, context=user_context)
                except json.JSONDecodeError:
                    await websocket.send_json({"error": "Invalid JSON format."})
        except WebSocketDisconnect:
            manager.disconnect(websocket)
