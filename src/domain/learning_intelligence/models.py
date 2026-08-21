"""Learning Intelligence domain SQLAlchemy models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from src.domain.auth.models import User
    from src.domain.learning.models import Concept, Skill


class ConceptReviewState(BaseModel):
    """SuperMemo-2 spaced repetition state for a concept and user."""

    __tablename__ = "concept_review_states"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(String(36), ForeignKey("concepts.id"), nullable=False, index=True)

    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    next_review_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "concept_id", name="uq_user_concept_review_state"),)

    if TYPE_CHECKING:
        user: Mapped[User]
        concept: Mapped[Concept]
    else:
        user = relationship("User")
        concept = relationship("Concept")


class SkillMastery(BaseModel):
    """Skill mastery tracking for a user."""

    __tablename__ = "skill_mastery"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id"), nullable=False, index=True)

    mastery_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill_mastery"),)

    if TYPE_CHECKING:
        user: Mapped[User]
        skill: Mapped[Skill]
    else:
        user = relationship("User")
        skill = relationship("Skill")


class ReviewLog(BaseModel):
    """Historical log of review events."""

    __tablename__ = "review_logs"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(String(36), ForeignKey("concepts.id"), nullable=False, index=True)

    quality: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-5 SM2 scale
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    if TYPE_CHECKING:
        user: Mapped[User]
        concept: Mapped[Concept]
    else:
        user = relationship("User")
        concept = relationship("Concept")
