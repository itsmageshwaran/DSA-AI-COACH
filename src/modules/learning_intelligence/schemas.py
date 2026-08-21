from pydantic import BaseModel, Field
from datetime import datetime


class ConceptReviewStateResponse(BaseModel):
    id: str
    user_id: str
    concept_id: str
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review_date: datetime
    last_reviewed_at: datetime | None

    model_config = {"from_attributes": True}


class ReviewRequest(BaseModel):
    grade: int = Field(..., ge=0, le=5, description="Grade from 0 to 5 based on SM-2")


class ReviewResponse(BaseModel):
    status: str
    concept_id: str
    next_review_date: datetime
    ease_factor: float


class SkillMasteryResponse(BaseModel):
    id: str
    skill_id: str
    mastery_level: float
    last_activity_at: datetime

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    due_concept_ids: list[str]
