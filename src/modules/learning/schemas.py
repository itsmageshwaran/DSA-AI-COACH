"""Pydantic schemas for Learning Domain."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


# Learning Path Schemas
class LearningPathCreate(BaseModel):
    """Schema for creating a learning path."""

    title: str = Field(..., max_length=255)
    description: str | None = None
    is_published: bool = True


class LearningPathResponse(BaseModel):
    """Schema for returning a learning path."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None = None
    is_published: bool
    created_at: datetime


# Course Schemas
class CourseCreate(BaseModel):
    """Schema for creating a course."""

    title: str = Field(..., max_length=255)
    description: str | None = None
    learning_path_id: str | None = None


class CourseResponse(BaseModel):
    """Schema for returning a course."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None = None
    learning_path_id: str | None = None
    created_at: datetime


# Module Schemas
class ModuleCreate(BaseModel):
    """Schema for creating a module."""

    title: str = Field(..., max_length=255)
    description: str | None = None
    order: int = 1
    course_id: str


class ModuleResponse(BaseModel):
    """Schema for returning a module."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None = None
    order: int
    course_id: str
    created_at: datetime


# Concept & Skill Schemas
class ConceptCreate(BaseModel):
    """Schema for creating a concept."""

    name: str = Field(..., max_length=255)
    description: str | None = None


class ConceptResponse(BaseModel):
    """Schema for returning a concept."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    created_at: datetime


class SkillCreate(BaseModel):
    """Schema for creating a skill."""

    name: str = Field(..., max_length=255)
    description: str | None = None


class SkillResponse(BaseModel):
    """Schema for returning a skill."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    created_at: datetime


# Lesson Schemas
class LessonCreate(BaseModel):
    """Schema for creating a lesson."""

    title: str = Field(..., max_length=255)
    content: str
    order: int = 1
    module_id: str
    concept_id: str | None = None
    skill_id: str | None = None


class LessonResponse(BaseModel):
    """Schema for returning a lesson."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    content: str
    order: int
    module_id: str
    concept_id: str | None = None
    skill_id: str | None = None
    created_at: datetime


# Exercise Schemas
class ExerciseCreate(BaseModel):
    """Schema for creating an exercise."""

    title: str = Field(..., max_length=255)
    instructions: str
    starter_code: str | None = None
    lesson_id: str


class ExerciseResponse(BaseModel):
    """Schema for returning an exercise."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    instructions: str
    starter_code: str | None = None
    lesson_id: str
    difficulty: str | None = None
    concept_name: str | None = None
    is_completed: bool = False
    test_cases_json: Any = None
    entrypoint: str | None = None
    created_at: datetime


# Enrollment Schemas
class EnrollmentCreate(BaseModel):
    """Schema for creating an enrollment."""

    learning_path_id: str


class EnrollmentResponse(BaseModel):
    """Schema for returning an enrollment."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    learning_path_id: str
    completed: bool
    created_at: datetime


# Progress Schemas
class ProgressCreate(BaseModel):
    """Schema for recording progress."""

    lesson_id: str
    completed: bool = True
    score: float | None = Field(None, ge=0.0, le=100.0)


class ProgressResponse(BaseModel):
    """Schema for returning progress."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    lesson_id: str
    completed: bool
    score: float | None = None
    completed_at: datetime | None = None
    created_at: datetime


class ProgressSummaryResponse(BaseModel):
    """Schema for progress summary statistics."""

    user_id: str
    total_lessons_completed: int
    completion_percentage: float
    average_score: float | None = None


class ConceptMasteryResponse(BaseModel):
    """Schema for concept mastery statistics."""

    concept_id: str
    concept_name: str
    mastery_percentage: float
    completed_lessons: int
    total_lessons: int


# Submission Schemas
class SubmissionCreate(BaseModel):
    """Schema for exercise submission."""

    exercise_id: str
    code: str


class AchievementResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    icon: str | None = None

class SubmissionResponse(BaseModel):
    """Schema for returning a submission."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    exercise_id: str
    code: str
    status: str
    feedback: str | None = None
    created_at: datetime
    new_achievements: list[AchievementResponse] | None = None

class RecommendationResponse(BaseModel):
    exercise_id: str | None = None
    title: str
    difficulty: str
    concept: str
    roadmap_phase: str
    reason: str
