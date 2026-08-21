"""Users module Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileBase(BaseModel):
    career_goal: str | None = None
    experience_level: str | None = None
    preferred_language: str | None = None
    onboarding_completed: bool = False

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: str

class UserResponse(BaseModel):
    """User profile response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    role: str | None = None
    profile: UserProfileResponse | None = None
    created_at: datetime
