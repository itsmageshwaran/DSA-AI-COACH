"""Database models entrypoint re-exporting all domain models for Alembic."""

from __future__ import annotations

from src.domain.auth.models import RefreshToken, Role, User, UserProfile
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
    Achievement,
    UserAchievement,
)
from src.domain.learning_intelligence.models import (
    ConceptReviewState,
    ReviewLog,
    SkillMastery,
)
from src.domain.billing.models import (
    AuditLog,
    Organization,
    OrganizationMember,
    Subscription,
    SubscriptionPlan,
    UsageRecord,
)
from src.infrastructure.database.base import Base, BaseModel

__all__ = [
    "Achievement",
    "AuditLog",
    "Base",
    "BaseModel",
    "Concept",
    "ConceptReviewState",
    "Course",
    "Enrollment",
    "Exercise",
    "LearningPath",
    "Lesson",
    "Module",
    "Organization",
    "OrganizationMember",
    "Progress",
    "RefreshToken",
    "ReviewLog",
    "Role",
    "Skill",
    "SkillMastery",
    "Submission",
    "Subscription",
    "SubscriptionPlan",
    "UsageRecord",
    "User",
    "UserAchievement",
    "UserProfile",
]
