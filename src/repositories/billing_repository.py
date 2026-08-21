"""Billing repository for subscriptions, usage, and organizations."""

from __future__ import annotations

from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.billing.models import (
    AuditLog,
    Organization,
    OrganizationMember,
    Subscription,
    SubscriptionPlan,
    UsageRecord,
)


class BillingRepository:
    """Repository for billing and organization entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_plan_by_name(self, name: str) -> SubscriptionPlan | None:
        """Get a subscription plan by its name (e.g., FREE, PRO)."""
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_organizations(self, user_id: str) -> Sequence[Organization]:
        """Get all active organizations a user is a member of."""
        stmt = (
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id, Organization.is_active)
            .options(selectinload(Organization.subscription).selectinload(Subscription.plan))
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_active_subscription_for_user(self, user_id: str) -> Subscription | None:
        """Resolve active subscription for a user.

        Checks if the user has an active Organization subscription first.
        If not, falls back to their personal subscription.
        """
        # 1. Check organization subscriptions
        org_stmt = (
            select(Subscription)
            .join(Organization, Subscription.organization_id == Organization.id)
            .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
            .where(
                OrganizationMember.user_id == user_id,
                Organization.is_active,
                Subscription.status == "active",
            )
            .options(selectinload(Subscription.plan))
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        org_sub = (await self._session.execute(org_stmt)).scalar_one_or_none()
        if org_sub:
            return org_sub

        # 2. Check personal subscription
        personal_stmt = (
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.status == "active",
            )
            .options(selectinload(Subscription.plan))
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        return (await self._session.execute(personal_stmt)).scalar_one_or_none()

    def add_usage_record(self, record: UsageRecord) -> None:
        """Add a usage record to the session."""
        self._session.add(record)

    def add_audit_log(self, log: AuditLog) -> None:
        """Add an audit log to the session."""
        self._session.add(log)
