"""Lessons API endpoints (/api/v1/lessons)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.auth.models import User
from src.domain.learning.models import Lesson
from src.infrastructure.database.dependencies import get_unit_of_work
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import LessonRepository
from src.modules.auth.dependencies import get_current_active_user, require_role
from src.modules.learning.schemas import LessonCreate, LessonResponse

router = APIRouter()


@router.get("", response_model=list[LessonResponse], summary="List all lessons")
async def list_lessons(
    module_id: str | None = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> list[LessonResponse]:
    """Retrieve all lessons or filter by module_id."""
    repo = LessonRepository(uow.session)
    if module_id:
        lessons = await repo.get_by_module(module_id)
    else:
        lessons = await repo.get_all()
    return [LessonResponse.model_validate(lesn) for lesn in lessons]


@router.post(
    "",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lesson",
)
async def create_lesson(
    payload: LessonCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(require_role("admin")),
) -> LessonResponse:
    """Create a new lesson (Admin only)."""
    repo = LessonRepository(uow.session)
    lesson = Lesson(
        title=payload.title,
        content=payload.content,
        order=payload.order,
        module_id=payload.module_id,
        concept_id=payload.concept_id,
        skill_id=payload.skill_id,
    )
    created = await repo.create(lesson)
    await uow.commit()
    return LessonResponse.model_validate(created)


@router.get("/{lesson_id}", response_model=LessonResponse, summary="Get lesson by ID")
async def get_lesson(
    lesson_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> LessonResponse:
    """Retrieve lesson by unique ID."""
    repo = LessonRepository(uow.session)
    lesson = await repo.get_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return LessonResponse.model_validate(lesson)
