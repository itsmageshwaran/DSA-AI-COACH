"""FastAPI router for AI Gateway model completion and Socratic tutoring endpoints."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import User
from src.infrastructure.database.dependencies import get_db_session
from src.modules.auth.dependencies import get_current_active_user
from src.modules.ai.schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    SocraticHintRequest,
    SocraticHintResponse,
)
from src.modules.ai.service import ai_service

router = APIRouter()


@router.post(
    "/generate",
    name="ai-generate",
    status_code=status.HTTP_200_OK,
    response_model=AIGenerateResponse,
    tags=["AI Gateway"],
)
async def generate_completion(
    request: AIGenerateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AIGenerateResponse:
    """Generate LLM response through AI Gateway with input guardrail validation."""
    return await ai_service.generate_completion(user_id=current_user.id, request=request, session=db)


@router.post(
    "/socratic-hint",
    name="ai-socratic-hint",
    status_code=status.HTTP_200_OK,
    response_model=SocraticHintResponse,
    tags=["AI Gateway"],
)
async def generate_socratic_hint(
    request: SocraticHintRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SocraticHintResponse:
    """Generate Socratic hint for exercise code submission."""
    return await ai_service.generate_socratic_hint(user_id=current_user.id, request=request, session=db)


@router.post(
    "/generate/stream",
    name="ai-generate-stream",
    tags=["AI Gateway"],
)
async def generate_stream(
    request: AIGenerateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> StreamingResponse:
    """Stream AI token generation response using Server-Sent Events (SSE)."""

    async def sse_event_generator() -> AsyncGenerator[str, None]:
        async for chunk in ai_service.generate_stream(user_id=current_user.id, request=request, session=db):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse_event_generator(), media_type="text/event-stream")
