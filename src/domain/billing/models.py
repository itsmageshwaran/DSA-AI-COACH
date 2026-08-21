"""Billing, Quota, and Enterprise Tenancy SQLAlchemy Models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from src.domain.auth.models import User


class Organization(BaseModel):
    """Enterprise organization for B2B tenancy."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    members: Mapped[list[OrganizationMember]] = relationship(
        "OrganizationMember", back_populates="organization", cascade="all, delete-orphan"
    )
    subscription: Mapped[Subscription | None] = relationship(
        "Subscription", back_populates="organization", uselist=False, cascade="all, delete-orphan"
    )


class OrganizationMember(BaseModel):
    """Membership mapping a User to an Organization with a role."""

    __tablename__ = "organization_members"

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")  # "owner", "admin", "member"

    organization: Mapped[Organization] = relationship("Organization", back_populates="members")
    user: Mapped[User] = relationship("User", primaryjoin="User.id == OrganizationMember.user_id")

    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_org_member"),)


class SubscriptionPlan(BaseModel):
    """Defines limits and features for a plan (Free, Pro, Enterprise)."""

    __tablename__ = "subscription_plans"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Store dynamic limits (e.g., {"ai_requests_daily": 100, "code_executions_daily": 500})
    limits: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    features: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    subscriptions: Mapped[list[Subscription]] = relationship("Subscription", back_populates="plan")


class Subscription(BaseModel):
    """A user or organization's active subscription."""

    __tablename__ = "subscriptions"

    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("subscription_plans.id"), nullable=False)

    # Either user_id OR organization_id must be set, not both.
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    organization_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active, canceled, past_due
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    provider_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    plan: Mapped[SubscriptionPlan] = relationship("SubscriptionPlan", back_populates="subscriptions")
    user: Mapped[User | None] = relationship("User", primaryjoin="User.id == Subscription.user_id")
    organization: Mapped[Organization | None] = relationship("Organization", back_populates="subscription")


class UsageRecord(BaseModel):
    """Append-only log of resource consumption."""

    __tablename__ = "usage_records"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )

    resource_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g., "ai_requests", "code_executions"
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)

    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_info: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class AuditLog(BaseModel):
    """Immutable log of security/business events."""

    __tablename__ = "audit_logs"

    actor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    organization_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )

    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    metadata_info: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
