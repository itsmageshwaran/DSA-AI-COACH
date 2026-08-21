"""Recommendations and Roadmap API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import User
from src.infrastructure.database.session import get_async_session
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.modules.auth.dependencies import get_current_active_user
from src.modules.learning.roadmap_service import RoadmapService
from src.modules.learning.schemas import RecommendationResponse

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/roadmap", status_code=status.HTTP_200_OK, summary="Get personalized career roadmap")
async def get_roadmap(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """Retrieve personalized roadmap based on user's career goal."""
    async with UnitOfWork(session) as uow:
        return await RoadmapService.generate_roadmap(uow, current_user.id)

@router.get("/next-problem", response_model=RecommendationResponse, status_code=status.HTTP_200_OK, summary="Get the next best problem")
async def get_next_problem(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """Determine the next best problem based on roadmap and difficulty progression."""
    # We will implement the recommendation engine here (Phase 7)
    from src.modules.learning.recommendation_service import RecommendationService
    async with UnitOfWork(session) as uow:
        return await RecommendationService.get_next_problem(uow, current_user.id)
