"""Unit tests for Learning Domain Repositories."""

from __future__ import annotations

import pytest
from src.domain.learning.models import Concept, Course, LearningPath, Module, Skill
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import (
    ConceptRepository,
    CourseRepository,
    LearningPathRepository,
    ModuleRepository,
    SkillRepository,
)


@pytest.mark.anyio
async def test_learning_path_course_module_repositories() -> None:
    """Test CRUD operations for LearningPath, Course, and Module repositories."""
    async with UnitOfWork() as uow:
        lp_repo = LearningPathRepository(uow.session)
        lp = await lp_repo.create(LearningPath(title="DSA Foundations", description="Core DSA"))

        course_repo = CourseRepository(uow.session)
        course = await course_repo.create(Course(title="Arrays & Strings", learning_path_id=lp.id))

        mod_repo = ModuleRepository(uow.session)
        await mod_repo.create(Module(title="Two Pointers", order=1, course_id=course.id))
        await mod_repo.create(Module(title="Sliding Window", order=2, course_id=course.id))

        await uow.commit()

        modules = await mod_repo.get_by_course(course.id)
        assert len(modules) == 2
        assert modules[0].title == "Two Pointers"
        assert modules[1].title == "Sliding Window"


@pytest.mark.anyio
async def test_concept_and_skill_repositories() -> None:
    """Test Concept and Skill repositories."""
    async with UnitOfWork() as uow:
        c_repo = ConceptRepository(uow.session)
        concept = await c_repo.create(Concept(name="Binary Search", description="Divide and conquer search"))

        s_repo = SkillRepository(uow.session)
        skill = await s_repo.create(Skill(name="Problem Decomposition"))

        await uow.commit()

        fetched_c = await c_repo.get_by_name("Binary Search")
        assert fetched_c is not None
        assert fetched_c.id == concept.id

        fetched_s = await s_repo.get_by_name("Problem Decomposition")
        assert fetched_s is not None
        assert fetched_s.id == skill.id
