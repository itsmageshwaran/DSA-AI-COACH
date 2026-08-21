"""LearningPaths API endpoints (/api/v1/learning-paths)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.auth.models import User
from src.domain.learning.models import LearningPath
from src.infrastructure.database.dependencies import get_unit_of_work
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import LearningPathRepository
from src.modules.auth.dependencies import get_current_active_user, require_role
from src.modules.learning.schemas import (
    EnrollmentResponse,
    LearningPathCreate,
    LearningPathResponse,
)
from src.modules.learning.service import enroll_user_in_path

router = APIRouter()


@router.get("", response_model=list[LearningPathResponse], summary="List all learning paths")
async def list_learning_paths(
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> list[LearningPathResponse]:
    """Retrieve all learning paths."""
    repo = LearningPathRepository(uow.session)
    paths = await repo.get_all()
    return [LearningPathResponse.model_validate(p) for p in paths]


@router.post(
    "",
    response_model=LearningPathResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new learning path",
)
async def create_learning_path(
    payload: LearningPathCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(require_role("admin")),
) -> LearningPathResponse:
    """Create a new learning path (Admin only)."""
    repo = LearningPathRepository(uow.session)
    path = LearningPath(
        title=payload.title,
        description=payload.description,
        is_published=payload.is_published,
    )
    created = await repo.create(path)
    await uow.commit()
    return LearningPathResponse.model_validate(created)


@router.get("/{path_id}", response_model=LearningPathResponse, summary="Get learning path by ID")
async def get_learning_path(
    path_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> LearningPathResponse:
    """Retrieve learning path by ID."""
    repo = LearningPathRepository(uow.session)
    path = await repo.get_by_id(path_id)
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found")
    return LearningPathResponse.model_validate(path)


@router.post(
    "/{path_id}/enroll",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll in a learning path",
)
async def enroll_in_path(
    path_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> EnrollmentResponse:
    """Enroll current active user in a learning path."""
    enrollment = await enroll_user_in_path(uow, user_id=current_user.id, learning_path_id=path_id)
    return EnrollmentResponse.model_validate(enrollment)
