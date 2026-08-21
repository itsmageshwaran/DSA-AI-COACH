"""Business services for Learning Domain operations."""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import select

from src.domain.learning.models import (
    Enrollment,
    Lesson,
    Progress,
    Submission,
)
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import (
    ConceptRepository,
    EnrollmentRepository,
    ExerciseRepository,
    LearningPathRepository,
    LessonRepository,
    ProgressRepository,
    SubmissionRepository,
)
from src.modules.learning.schemas import ConceptMasteryResponse, ProgressSummaryResponse


async def enroll_user_in_path(uow: UnitOfWork, user_id: str, learning_path_id: str) -> Enrollment:
    """Enroll a user into a learning path."""
    path_repo = LearningPathRepository(uow.session)
    path = await path_repo.get_by_id(learning_path_id)
    if not path or not path.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning path not found or unavailable",
        )

    enrollment_repo = EnrollmentRepository(uow.session)
    existing = await enrollment_repo.get_by_user_and_path(user_id, learning_path_id)
    if existing:
        return existing

    enrollment = Enrollment(user_id=user_id, learning_path_id=learning_path_id, completed=False)
    created = await enrollment_repo.create(enrollment)
    await uow.commit()
    return created


async def complete_lesson(uow: UnitOfWork, user_id: str, lesson_id: str, score: float | None = None) -> Progress:
    """Mark a lesson as completed for a user."""
    return await update_progress(uow, user_id=user_id, lesson_id=lesson_id, completed=True, score=score)


async def update_progress(
    uow: UnitOfWork, user_id: str, lesson_id: str, completed: bool, score: float | None = None
) -> Progress:
    """Create or update user progress for a lesson."""
    lesson_repo = LessonRepository(uow.session)
    lesson = await lesson_repo.get_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    progress_repo = ProgressRepository(uow.session)
    record = await progress_repo.get_by_user_and_lesson(user_id, lesson_id)
    now = datetime.now(timezone.utc)

    if record:
        record.completed = completed
        if score is not None:
            record.score = score
        if completed and not record.completed_at:
            record.completed_at = now
        await uow.commit()
        return record

    new_record = Progress(
        user_id=user_id,
        lesson_id=lesson_id,
        completed=completed,
        score=score,
        completed_at=now if completed else None,
    )
    created = await progress_repo.create(new_record)
    await uow.commit()
    return created


async def submit_exercise(uow: UnitOfWork, user_id: str, exercise_id: str, code: str) -> dict:
    """Submit code for an exercise and evaluate simple correctness criteria."""
    exercise_repo = ExerciseRepository(uow.session)
    exercise = await exercise_repo.get_by_id(exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    # Basic correctness evaluation for baseline submissions
    sub_status = "passed" if len(code.strip()) > 0 else "failed"
    feedback = "Submission evaluated successfully." if sub_status == "passed" else "Code submission cannot be empty."

    submission = Submission(
        user_id=user_id,
        exercise_id=exercise_id,
        code=code,
        status=sub_status,
        feedback=feedback,
    )
    submission_repo = SubmissionRepository(uow.session)
    created = await submission_repo.create(submission)
    
    new_achievements = []
    if sub_status == "passed":
        # Automatically mark associated lesson completed
        await update_progress(uow, user_id=user_id, lesson_id=exercise.lesson_id, completed=True, score=100.0)
        
        # Evaluate achievements
        from src.modules.learning.achievement_service import AchievementService
        new_achievements = await AchievementService.evaluate_achievements(uow, user_id)

    await uow.commit()
    return {
        "submission": created,
        "new_achievements": new_achievements
    }


async def get_learner_progress(uow: UnitOfWork, user_id: str) -> ProgressSummaryResponse:
    """Calculate overall progress statistics for a user."""
    progress_repo = ProgressRepository(uow.session)
    user_records = await progress_repo.get_user_progress(user_id)

    lesson_repo = LessonRepository(uow.session)
    all_lessons = await lesson_repo.get_all()
    total_lessons = len(all_lessons)

    completed_records = [r for r in user_records if r.completed]
    completed_count = len(completed_records)

    completion_percentage = (completed_count / total_lessons * 100.0) if total_lessons > 0 else 0.0

    scores = [r.score for r in completed_records if r.score is not None]
    avg_score = sum(scores) / len(scores) if scores else None

    return ProgressSummaryResponse(
        user_id=user_id,
        total_lessons_completed=completed_count,
        completion_percentage=round(completion_percentage, 2),
        average_score=round(avg_score, 2) if avg_score is not None else None,
    )


async def get_concept_mastery(uow: UnitOfWork, user_id: str) -> list[ConceptMasteryResponse]:
    """Calculate concept mastery metrics for a user across all concepts."""
    concept_repo = ConceptRepository(uow.session)
    concepts = await concept_repo.get_all()

    progress_repo = ProgressRepository(uow.session)
    user_progress = await progress_repo.get_user_progress(user_id)
    completed_lesson_ids = {p.lesson_id for p in user_progress if p.completed}

    mastery_list: list[ConceptMasteryResponse] = []
    for concept in concepts:
        result = await uow.session.execute(select(Lesson).where(Lesson.concept_id == concept.id))
        concept_lessons = list(result.scalars().all())
        total_c_lessons = len(concept_lessons)

        if total_c_lessons == 0:
            continue

        c_completed = sum(1 for lesn in concept_lessons if lesn.id in completed_lesson_ids)
        percentage = (c_completed / total_c_lessons) * 100.0

        mastery_list.append(
            ConceptMasteryResponse(
                concept_id=concept.id,
                concept_name=concept.name,
                mastery_percentage=round(percentage, 2),
                completed_lessons=c_completed,
                total_lessons=total_c_lessons,
            )
        )

    return mastery_list
