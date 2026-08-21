"""Exercises API endpoints (/api/v1/exercises)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import User
from src.domain.learning.models import Exercise, Lesson, Concept, Progress
from src.infrastructure.database.dependencies import get_db_session
from src.modules.auth.dependencies import get_current_active_user
from src.modules.learning.schemas import ExerciseResponse

router = APIRouter()


from sqlalchemy.orm import selectinload

@router.get("", response_model=list[ExerciseResponse], summary="List all exercises")
async def list_exercises(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[ExerciseResponse]:
    """Retrieve all exercises."""
    from src.domain.learning.models import Lesson, Concept, Progress
    result = await db.execute(
        select(Exercise).options(
            selectinload(Exercise.lesson).selectinload(Lesson.concept)
        )
    )
    exercises = result.scalars().all()
    
    # Fetch user progress
    prog_result = await db.execute(select(Progress).where(Progress.user_id == current_user.id))
    completed_lesson_ids = {p.lesson_id for p in prog_result.scalars().all() if p.completed}
    
    responses = []
    for e in exercises:
        concept_name = e.lesson.concept.name if e.lesson and e.lesson.concept else "General"
        is_completed = e.lesson_id in completed_lesson_ids
        responses.append(ExerciseResponse(
            id=e.id,
            title=e.title,
            instructions=e.instructions,
            starter_code=e.starter_code,
            lesson_id=e.lesson_id,
            difficulty=e.difficulty,
            concept_name=concept_name,
            is_completed=is_completed,
            created_at=e.created_at
        ))
    return responses


@router.get("/{exercise_id}", response_model=ExerciseResponse, summary="Get exercise by ID")
async def get_exercise(
    exercise_id: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExerciseResponse:
    """Retrieve a specific exercise by ID."""
    stmt = (
        select(Exercise)
        .options(selectinload(Exercise.lesson).selectinload(Lesson.concept))
        .where(Exercise.id == exercise_id)
    )
    result = await db.execute(stmt)
    exercise = result.scalars().first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
        
    setattr(exercise, 'concept_name', exercise.lesson.concept.name if exercise.lesson and exercise.lesson.concept else None)
    setattr(exercise, 'is_completed', False) # Not tracking completion for single exercise fetch currently
        
    return ExerciseResponse.model_validate(exercise)

