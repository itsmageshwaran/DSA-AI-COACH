"""Submissions API endpoints (/api/v1/submissions)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.auth.models import User
from src.infrastructure.database.dependencies import get_unit_of_work
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import SubmissionRepository
from src.modules.auth.dependencies import get_current_active_user
from src.modules.learning.schemas import SubmissionCreate, SubmissionResponse
from src.modules.learning.service import submit_exercise

router = APIRouter()


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit exercise code solution",
)
async def create_submission(
    payload: SubmissionCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> SubmissionResponse:
    """Submit solution code for an exercise."""
    result = await submit_exercise(
        uow,
        user_id=current_user.id,
        exercise_id=payload.exercise_id,
        code=payload.code,
    )
    
    submission = result["submission"]
    new_achievements = result["new_achievements"]
    
    return SubmissionResponse(
        id=submission.id,
        user_id=submission.user_id,
        exercise_id=submission.exercise_id,
        code=submission.code,
        status=submission.status,
        feedback=submission.feedback,
        created_at=submission.created_at,
        new_achievements=new_achievements
    )


@router.get("/{submission_id}", response_model=SubmissionResponse, summary="Get submission by ID")
async def get_submission(
    submission_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> SubmissionResponse:
    """Retrieve submission details by ID."""
    repo = SubmissionRepository(uow.session)
    submission = await repo.get_by_id(submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return SubmissionResponse.model_validate(submission)
