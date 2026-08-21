"""Learning domain SQLAlchemy models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import BaseModel

from src.domain.auth.models import User


class LearningPath(BaseModel):
    """Learning path containing sequence of courses."""

    __tablename__ = "learning_paths"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    if TYPE_CHECKING:
        courses: Mapped[list[Course]]
        enrollments: Mapped[list[Enrollment]]
    else:
        courses = relationship("Course", back_populates="learning_path", cascade="all, delete-orphan")
        enrollments = relationship("Enrollment", back_populates="learning_path", cascade="all, delete-orphan")


class Course(BaseModel):
    """Course entity."""

    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    learning_path_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("learning_paths.id"), nullable=True)

    if TYPE_CHECKING:
        learning_path: Mapped[LearningPath | None]
        modules: Mapped[list[Module]]
    else:
        learning_path = relationship("LearningPath", back_populates="courses")
        modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")


class Module(BaseModel):
    """Module grouping within a course."""

    __tablename__ = "modules"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id"), nullable=False)

    if TYPE_CHECKING:
        course: Mapped[Course]
        lessons: Mapped[list[Lesson]]
    else:
        course = relationship("Course", back_populates="modules")
        lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")


class Concept(BaseModel):
    """Concept topic tracking."""

    __tablename__ = "concepts"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    if TYPE_CHECKING:
        lessons: Mapped[list[Lesson]]
    else:
        lessons = relationship("Lesson", back_populates="concept")


class Skill(BaseModel):
    """Skill taxonomy tracking."""

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    if TYPE_CHECKING:
        lessons: Mapped[list[Lesson]]
    else:
        lessons = relationship("Lesson", back_populates="skill")


class Lesson(BaseModel):
    """Lesson entity within a module."""

    __tablename__ = "lessons"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    module_id: Mapped[str] = mapped_column(String(36), ForeignKey("modules.id"), nullable=False)
    concept_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("concepts.id"), nullable=True)
    skill_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("skills.id"), nullable=True)

    if TYPE_CHECKING:
        module: Mapped[Module]
        concept: Mapped[Concept | None]
        skill: Mapped[Skill | None]
        exercises: Mapped[list[Exercise]]
        progress_records: Mapped[list[Progress]]
    else:
        module = relationship("Module", back_populates="lessons")
        concept = relationship("Concept", back_populates="lessons")
        skill = relationship("Skill", back_populates="lessons")
        exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan")
        progress_records = relationship("Progress", back_populates="lesson", cascade="all, delete-orphan")


class Exercise(BaseModel):
    """Coding exercise associated with a lesson."""

    __tablename__ = "exercises"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="easy", nullable=False)
    test_cases_json: Mapped[list[dict]] = mapped_column(JSON, default=list)
    entrypoint: Mapped[str] = mapped_column(String(100), default="solution")

    lesson_id: Mapped[str] = mapped_column(String(36), ForeignKey("lessons.id"), nullable=False)

    if TYPE_CHECKING:
        lesson: Mapped[Lesson]
        submissions: Mapped[list[Submission]]
    else:
        lesson = relationship("Lesson", back_populates="exercises")
        submissions = relationship("Submission", back_populates="exercise", cascade="all, delete-orphan")


class Achievement(BaseModel):
    """Achievement definitions."""

    __tablename__ = "achievements"

    type: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    if TYPE_CHECKING:
        user_achievements: Mapped[list[UserAchievement]]
    else:
        user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


class UserAchievement(BaseModel):
    """User earned achievements."""

    __tablename__ = "user_achievements"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    achievement_id: Mapped[str] = mapped_column(String(36), ForeignKey("achievements.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # Store related concepts, streaks, etc.

    if TYPE_CHECKING:
        user: Mapped[User]
        achievement: Mapped[Achievement]
    else:
        user = relationship("User")
        achievement = relationship("Achievement", back_populates="user_achievements")


class Enrollment(BaseModel):
    """User enrollment in a learning path."""

    __tablename__ = "enrollments"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    learning_path_id: Mapped[str] = mapped_column(String(36), ForeignKey("learning_paths.id"), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    if TYPE_CHECKING:
        user: Mapped[User]
        learning_path: Mapped[LearningPath]
    else:
        user = relationship("User")
        learning_path = relationship("LearningPath", back_populates="enrollments")


class Progress(BaseModel):
    """User progress tracking per lesson."""

    __tablename__ = "progress"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    lesson_id: Mapped[str] = mapped_column(String(36), ForeignKey("lessons.id"), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    if TYPE_CHECKING:
        user: Mapped[User]
        lesson: Mapped[Lesson]
    else:
        user = relationship("User")
        lesson = relationship("Lesson", back_populates="progress_records")


class Submission(BaseModel):
    """User submission for an exercise."""

    __tablename__ = "submissions"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    exercise_id: Mapped[str] = mapped_column(String(36), ForeignKey("exercises.id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    if TYPE_CHECKING:
        user: Mapped[User]
        exercise: Mapped[Exercise]
    else:
        user = relationship("User")
        exercise = relationship("Exercise", back_populates="submissions")



