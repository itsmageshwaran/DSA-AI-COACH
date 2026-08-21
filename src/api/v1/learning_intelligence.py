from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.modules.auth.dependencies import get_current_user
from src.domain.auth.models import User
from src.infrastructure.database.session import get_async_session
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.modules.learning_intelligence.schemas import (
    ReviewRequest,
    ReviewResponse,
    SkillMasteryResponse,
    RecommendationResponse,
    ConceptReviewStateResponse,
)
from src.modules.learning_intelligence.service import LearningIntelligenceService

router = APIRouter(prefix="/learning-intelligence", tags=["Learning Intelligence"])


@router.post("/concepts/{concept_id}/review", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
async def review_concept(
    concept_id: str,
    request: ReviewRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ReviewResponse:
    """Submit a review score (0-5) for a concept and schedule the next review."""
    async with UnitOfWork(session) as uow:
        try:
            state = await LearningIntelligenceService.record_concept_review(
                uow=uow, user_id=current_user.id, concept_id=concept_id, grade=request.grade
            )
            return ReviewResponse(
                status="success",
                concept_id=state.concept_id,
                next_review_date=state.next_review_date,
                ease_factor=state.ease_factor,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/reviews/due", response_model=list[ConceptReviewStateResponse])
async def get_due_reviews(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> list[ConceptReviewStateResponse]:
    """Get all concept reviews that are currently due."""
    async with UnitOfWork(session) as uow:
        states = await LearningIntelligenceService.get_due_reviews(uow, current_user.id)
        return [ConceptReviewStateResponse.model_validate(s, from_attributes=True) for s in states]


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 5,
    session: AsyncSession = Depends(get_async_session),
) -> RecommendationResponse:
    """Get ordered list of concepts to study next based on review intervals."""
    async with UnitOfWork(session) as uow:
        concept_ids = await LearningIntelligenceService.get_recommendations(uow, current_user.id, limit)
        return RecommendationResponse(due_concept_ids=concept_ids)


@router.get("/skills/{skill_id}/mastery", response_model=SkillMasteryResponse)
async def get_skill_mastery(
    skill_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> SkillMasteryResponse:
    """Calculate and return the updated mastery level for a specific skill."""
    async with UnitOfWork(session) as uow:
        mastery = await LearningIntelligenceService.update_skill_mastery(uow, current_user.id, skill_id)
        if not mastery:
            raise HTTPException(status_code=404, detail="Skill mastery not found")
        return SkillMasteryResponse.model_validate(mastery, from_attributes=True)
