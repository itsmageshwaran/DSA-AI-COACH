"""Auth Domain SQLAlchemy Models (User, Role, RefreshToken)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import BaseModel


class Role(BaseModel):
    """Role domain model for Role-Based Access Control (RBAC)."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    if TYPE_CHECKING:
        users: Mapped[list[User]]
    else:
        users = relationship("User", back_populates="role")


class User(BaseModel):
    """User domain model."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    role_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("roles.id"), nullable=True)

    if TYPE_CHECKING:
        role: Mapped[Role | None]
        refresh_tokens: Mapped[list[RefreshToken]]
        profile: Mapped[UserProfile | None]
    else:
        role = relationship("Role", back_populates="users")
        refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
        profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserProfile(BaseModel):
    """User profile for personalized learning path and goals."""

    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    career_goal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    if TYPE_CHECKING:
        user: Mapped[User]
    else:
        user = relationship("User", back_populates="profile")


class RefreshToken(BaseModel):
    """RefreshToken domain model for authentication sessions."""

    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    if TYPE_CHECKING:
        user: Mapped[User]
    else:
        user = relationship("User", back_populates="refresh_tokens")
