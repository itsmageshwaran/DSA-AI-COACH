"""Unit tests for Learning Domain Services."""

from __future__ import annotations

import pytest
from src.domain.auth.models import User
from src.domain.learning.models import Course, Exercise, LearningPath, Lesson, Module
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import (
    CourseRepository,
    EnrollmentRepository,
    ExerciseRepository,
    LearningPathRepository,
    LessonRepository,
    ModuleRepository,
    ProgressRepository,
)
from src.infrastructure.repositories.user_repository import UserRepository
from src.modules.learning.service import (
    enroll_user_in_path,
    submit_exercise,
)


@pytest.mark.anyio
async def test_enrollment_and_submission_services() -> None:
    """Test enrollment service and exercise submission service."""
    async with UnitOfWork() as uow:
        # Create user
        u_repo = UserRepository(uow.session)
        user = await u_repo.create(User(email="learner@example.com", hashed_password="hashed_pw"))

        # Create path, course, module, lesson, exercise
        lp = await LearningPathRepository(uow.session).create(LearningPath(title="Algo Path"))
        course = await CourseRepository(uow.session).create(Course(title="Sorting", learning_path_id=lp.id))
        module = await ModuleRepository(uow.session).create(Module(title="Quick Sort", course_id=course.id))
        lesson = await LessonRepository(uow.session).create(
            Lesson(title="Partition Logic", content="Content", module_id=module.id)
        )
        exercise = await ExerciseRepository(uow.session).create(
            Exercise(title="Implement Partition", instructions="Code partition", lesson_id=lesson.id)
        )
        await uow.commit()

        # Enroll user
        enrollment = await enroll_user_in_path(uow, user.id, lp.id)
        assert enrollment.user_id == user.id
        assert enrollment.learning_path_id == lp.id

        # Submit exercise
        sub_result = await submit_exercise(uow, user.id, exercise.id, "def partition(): pass")
        sub = sub_result["submission"]
        assert sub.status == "passed"
        
        # Verify progress recorded
        progress_repo = ProgressRepository(uow.session)
        user_progress = await progress_repo.get_user_progress(user.id)
        assert len(user_progress) == 1
        assert user_progress[0].lesson_id == lesson.id
        assert user_progress[0].completed is True
