"""Tests for progress calculations and concept mastery analytics."""

from __future__ import annotations

import pytest
from src.domain.auth.models import User
from src.domain.learning.models import Concept, Course, Lesson, Module
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import (
    ConceptRepository,
    CourseRepository,
    LessonRepository,
    ModuleRepository,
)
from src.infrastructure.repositories.user_repository import UserRepository
from src.modules.learning.service import (
    complete_lesson,
    get_concept_mastery,
    get_learner_progress,
)


@pytest.mark.anyio
async def test_learner_progress_and_concept_mastery_calculation() -> None:
    """Verify progress percentage, average score, and concept mastery calculations."""
    async with UnitOfWork() as uow:
        # Create user
        user = await UserRepository(uow.session).create(User(email="student@example.com", hashed_password="pw"))

        # Create Concept
        concept = await ConceptRepository(uow.session).create(Concept(name="Dynamic Programming"))

        # Create Course & Module
        course = await CourseRepository(uow.session).create(Course(title="DP Course"))
        module = await ModuleRepository(uow.session).create(Module(title="Memoization", course_id=course.id))

        # Create 4 lessons (2 linked to concept)
        l1 = await LessonRepository(uow.session).create(
            Lesson(title="Fibonacci DP", content="Content", module_id=module.id, concept_id=concept.id)
        )
        l2 = await LessonRepository(uow.session).create(
            Lesson(title="Grid Traveler", content="Content", module_id=module.id, concept_id=concept.id)
        )
        await LessonRepository(uow.session).create(Lesson(title="CanSum", content="Content", module_id=module.id))
        await LessonRepository(uow.session).create(Lesson(title="HowSum", content="Content", module_id=module.id))

        await uow.commit()

        # Complete l1 (score 80.0) and l2 (score 100.0)
        await complete_lesson(uow, user.id, l1.id, score=80.0)
        await complete_lesson(uow, user.id, l2.id, score=100.0)

        # 1. Test Learner Progress calculation
        progress_stats = await get_learner_progress(uow, user.id)
        assert progress_stats.total_lessons_completed == 2
        assert progress_stats.completion_percentage == 50.0  # 2 of 4 = 50.0%
        assert progress_stats.average_score == 90.0  # (80 + 100) / 2 = 90.0

        # 2. Test Concept Mastery calculation
        mastery_stats = await get_concept_mastery(uow, user.id)
        assert len(mastery_stats) == 1
        dp_mastery = mastery_stats[0]
        assert dp_mastery.concept_name == "Dynamic Programming"
        assert dp_mastery.completed_lessons == 2
        assert dp_mastery.total_lessons == 2
        assert dp_mastery.mastery_percentage == 100.0
