"""Async Repositories for Learning Domain entities."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.learning.models import (
    Concept,
    Course,
    Enrollment,
    Exercise,
    LearningPath,
    Lesson,
    Module,
    Progress,
    Skill,
    Submission,
)
from src.infrastructure.database.repository import Repository


class CourseRepository(Repository[Course]):
    """Repository for Course entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Course, session)


class ModuleRepository(Repository[Module]):
    """Repository for Module entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Module, session)

    async def get_by_course(self, course_id: str) -> list[Module]:
        """Fetch modules for a course ordered by position."""
        result = await self.session.execute(select(Module).where(Module.course_id == course_id).order_by(Module.order))
        return list(result.scalars().all())


class LessonRepository(Repository[Lesson]):
    """Repository for Lesson entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Lesson, session)

    async def get_by_module(self, module_id: str) -> list[Lesson]:
        """Fetch lessons for a module ordered by position."""
        result = await self.session.execute(select(Lesson).where(Lesson.module_id == module_id).order_by(Lesson.order))
        return list(result.scalars().all())


class LearningPathRepository(Repository[LearningPath]):
    """Repository for LearningPath entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LearningPath, session)


class EnrollmentRepository(Repository[Enrollment]):
    """Repository for Enrollment entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Enrollment, session)

    async def get_by_user_and_path(self, user_id: str, learning_path_id: str) -> Enrollment | None:
        """Fetch enrollment record for user and learning path."""
        result = await self.session.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.learning_path_id == learning_path_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_enrollments(self, user_id: str) -> list[Enrollment]:
        """Fetch all enrollments for a user."""
        result = await self.session.execute(select(Enrollment).where(Enrollment.user_id == user_id))
        return list(result.scalars().all())


class ProgressRepository(Repository[Progress]):
    """Repository for Progress entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Progress, session)

    async def get_by_user_and_lesson(self, user_id: str, lesson_id: str) -> Progress | None:
        """Fetch progress record for user and lesson."""
        result = await self.session.execute(
            select(Progress).where(
                Progress.user_id == user_id,
                Progress.lesson_id == lesson_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_progress(self, user_id: str) -> list[Progress]:
        """Fetch all progress records for a user."""
        result = await self.session.execute(select(Progress).where(Progress.user_id == user_id))
        return list(result.scalars().all())


class SkillRepository(Repository[Skill]):
    """Repository for Skill entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Skill, session)

    async def get_by_name(self, name: str) -> Skill | None:
        """Fetch skill by unique name."""
        result = await self.session.execute(select(Skill).where(Skill.name == name))
        return result.scalar_one_or_none()


class ConceptRepository(Repository[Concept]):
    """Repository for Concept entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Concept, session)

    async def get_by_name(self, name: str) -> Concept | None:
        """Fetch concept by unique name."""
        result = await self.session.execute(select(Concept).where(Concept.name == name))
        return result.scalar_one_or_none()


class ExerciseRepository(Repository[Exercise]):
    """Repository for Exercise entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Exercise, session)

    async def get_by_lesson(self, lesson_id: str) -> list[Exercise]:
        """Fetch exercises for a lesson."""
        result = await self.session.execute(select(Exercise).where(Exercise.lesson_id == lesson_id))
        return list(result.scalars().all())


class SubmissionRepository(Repository[Submission]):
    """Repository for Submission entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Submission, session)

    async def get_by_user_and_exercise(self, user_id: str, exercise_id: str) -> list[Submission]:
        """Fetch submissions for a user and exercise."""
        result = await self.session.execute(
            select(Submission).where(
                Submission.user_id == user_id,
                Submission.exercise_id == exercise_id,
            )
        )
        return list(result.scalars().all())
