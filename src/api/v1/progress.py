"""Progress API endpoints (/api/v1/progress)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.domain.auth.models import User
from src.infrastructure.database.dependencies import get_unit_of_work
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.modules.auth.dependencies import get_current_active_user
from src.modules.learning.schemas import (
    ConceptMasteryResponse,
    ProgressCreate,
    ProgressResponse,
    ProgressSummaryResponse,
)
from src.modules.learning.service import (
    get_concept_mastery,
    get_learner_progress,
    update_progress,
)

router = APIRouter()


@router.get("/me", response_model=ProgressSummaryResponse, summary="Get learner progress summary")
async def get_my_progress(
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> ProgressSummaryResponse:
    """Retrieve overall progress stats for current user."""
    return await get_learner_progress(uow, current_user.id)


@router.get("/me/concepts", response_model=list[ConceptMasteryResponse], summary="Get concept mastery metrics")
async def get_my_concept_mastery(
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> list[ConceptMasteryResponse]:
    """Retrieve concept mastery percentages for current user."""
    return await get_concept_mastery(uow, current_user.id)


@router.post(
    "",
    response_model=ProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Record or update lesson progress",
)
async def record_progress(
    payload: ProgressCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> ProgressResponse:
    """Record or update lesson completion status and score."""
    record = await update_progress(
        uow,
        user_id=current_user.id,
        lesson_id=payload.lesson_id,
        completed=payload.completed,
        score=payload.score,
    )
    return ProgressResponse.model_validate(record)

from src.modules.learning.schemas import AchievementResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domain.learning.models import UserAchievement, Achievement

@router.get("/me/achievements", response_model=list[AchievementResponse], summary="Get unlocked achievements")
async def get_my_achievements(
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> list[AchievementResponse]:
    """Retrieve unlocked achievements for the current user."""
    stmt = (
        select(UserAchievement)
        .options(selectinload(UserAchievement.achievement))
        .where(UserAchievement.user_id == current_user.id)
        .order_by(UserAchievement.earned_at.desc())
    )
    result = await uow.session.execute(stmt)
    records = result.scalars().all()
    
    return [
        AchievementResponse(
            achievement_type=r.achievement.achievement_type,
            name=r.achievement.name,
            description=r.achievement.description,
            icon_name=r.achievement.icon_name,
            earned_at=r.earned_at.isoformat()
        )
        for r in records
    ]
