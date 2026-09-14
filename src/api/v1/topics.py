"""Topics API endpoints for structured learning journey previews (/api/v1/topics)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import User
from src.infrastructure.database.session import get_async_session
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.modules.auth.dependencies import get_current_active_user
from src.modules.learning.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["Topic Learning"])


@router.get("/{topic_identifier}", status_code=status.HTTP_200_OK, summary="Get full topic learning experience")
async def get_topic_preview(
    topic_identifier: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """Retrieve full structured 4-phase learning journey for a DSA concept."""
    preferred_lang = (
        current_user.profile.preferred_language
        if current_user.profile and current_user.profile.preferred_language
        else "python"
    )
    async with UnitOfWork(session) as uow:
        return await TopicService.get_topic_learning_data(
            uow=uow,
            topic_identifier=topic_identifier,
            user_id=current_user.id,
            preferred_language=preferred_lang
        )
