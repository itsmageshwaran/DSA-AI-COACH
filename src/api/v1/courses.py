"""Courses API endpoints (/api/v1/courses)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.auth.models import User
from src.domain.learning.models import Course
from src.infrastructure.database.dependencies import get_unit_of_work
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import CourseRepository
from src.modules.auth.dependencies import get_current_active_user, require_role
from src.modules.learning.schemas import CourseCreate, CourseResponse

router = APIRouter()


@router.get("", response_model=list[CourseResponse], summary="List all courses")
async def list_courses(
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> list[CourseResponse]:
    """Retrieve all available courses."""
    repo = CourseRepository(uow.session)
    courses = await repo.get_all()
    return [CourseResponse.model_validate(c) for c in courses]


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new course",
)
async def create_course(
    payload: CourseCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(require_role("admin")),
) -> CourseResponse:
    """Create a new course (Admin only)."""
    repo = CourseRepository(uow.session)
    course = Course(
        title=payload.title,
        description=payload.description,
        learning_path_id=payload.learning_path_id,
    )
    created = await repo.create(course)
    await uow.commit()
    return CourseResponse.model_validate(created)


@router.get("/{course_id}", response_model=CourseResponse, summary="Get course by ID")
async def get_course(
    course_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> CourseResponse:
    """Retrieve course by unique ID."""
    repo = CourseRepository(uow.session)
    course = await repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return CourseResponse.model_validate(course)
