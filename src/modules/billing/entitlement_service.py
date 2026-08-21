"""Entitlement and Quota Service for Billing and SaaS limits."""

from __future__ import annotations

import datetime
from typing import Any

from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.redis.connection import get_redis_client
from src.repositories.billing_repository import BillingRepository
from src.domain.billing.models import UsageRecord

# Lua script for atomic quota check and consumption.
# Returns {1, new_usage} if successful, {0, current_usage} if quota exceeded.
# Limit == -1 implies unlimited.
CONSUME_QUOTA_LUA = """
local quota_key = KEYS[1]
local limit = tonumber(ARGV[1])
local amount = tonumber(ARGV[2])
local period_seconds = tonumber(ARGV[3])

if limit == -1 then
    return {1, 0}
end

local current_usage = tonumber(redis.call("GET", quota_key) or "0")

if current_usage + amount > limit then
    return {0, current_usage}
end

local new_usage = redis.call("INCRBY", quota_key, amount)

if current_usage == 0 and period_seconds > 0 then
    redis.call("EXPIRE", quota_key, period_seconds)
end

return {1, new_usage}
"""


class QuotaExceededError(Exception):
    """Raised when a user exceeds their subscription quota."""

    def __init__(self, resource: str, limit: int, current: int):
        self.resource = resource
        self.limit = limit
        self.current = current
        super().__init__(f"Quota exceeded for {resource}. Limit: {limit}, Current: {current}")


class EntitlementService:
    """Centralized service for SaaS entitlements and atomic quota consumption."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.redis = get_redis_client()
        self._lua_script_sha: str | None = None

    async def _get_lua_script(self) -> Any:
        """Register or retrieve Lua script in Redis."""
        if not self.redis:
            return None

        if not self._lua_script_sha:
            self._lua_script_sha = await self.redis.script_load(CONSUME_QUOTA_LUA)
        return self._lua_script_sha

    async def resolve_limits(self, user_id: str) -> dict[str, int]:
        """Resolve the active subscription limits for a user.

        Falls back to a default "FREE" plan if no active subscription exists.
        """
        repo = BillingRepository(self.uow.session)
        sub = await repo.get_active_subscription_for_user(user_id)

        if sub and sub.plan:
            return sub.plan.limits

        # Fallback to FREE plan limits
        free_plan = await repo.get_plan_by_name("FREE")
        if free_plan:
            return free_plan.limits

        # Hardcoded safe fallback for standard/free tier
        return {
            "ai_requests_daily": 500,
            "ai_tokens_daily": 500000,
            "code_executions_daily": 1000,
            "tutor_messages_daily": 500,
        }

    def _get_quota_key(self, subject_id: str, resource: str) -> str:
        """Generate a daily deterministic quota key."""
        today = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
        return f"quota:{subject_id}:{resource}:daily:{today}"

    async def consume_quota(
        self,
        user_id: str,
        resource: str,
        amount: int = 1,
        organization_id: str | None = None,
        request_id: str | None = None,
        metadata_info: dict[str, Any] | None = None,
    ) -> None:
        """Atomically consume quota and record usage.

        Raises QuotaExceededError if limit is reached.
        """
        limits = await self.resolve_limits(user_id)
        limit = limits.get(f"{resource}_daily", 0)  # default to 0 if not defined

        if limit == 0:
            raise QuotaExceededError(resource=resource, limit=0, current=0)

        subject_id = organization_id if organization_id else user_id

        if self.redis:
            # Atomic check-and-consume via Redis
            script_sha = await self._get_lua_script()
            quota_key = self._get_quota_key(subject_id, resource)

            # ARGV: [limit, amount, period_seconds (86400 for daily)]
            result_raw = await self.redis.evalsha(script_sha, 1, quota_key, str(limit), str(amount), "86400")  # type: ignore[misc]
            result = list(result_raw) if isinstance(result_raw, (list, tuple)) else [0, 0]
            success, new_usage = int(result[0]), int(result[1])

            if success == 0:
                raise QuotaExceededError(resource=resource, limit=limit, current=new_usage)
        else:
            # Safe Fallback (allow if Redis is down, or implement strict DB check)
            # We fail open if Redis is down to not block users, but we still log usage.
            pass

        # Record usage
        repo = BillingRepository(self.uow.session)
        usage = UsageRecord(
            user_id=user_id,
            organization_id=organization_id,
            resource_type=resource,
            quantity=amount,
            request_id=request_id,
            metadata_info=metadata_info or {},
        )
        repo.add_usage_record(usage)
        await self.uow.commit()

    async def check_access(self, user_id: str, feature: str) -> bool:
        """Check if a specific feature is enabled in the user's plan."""
        repo = BillingRepository(self.uow.session)
        sub = await repo.get_active_subscription_for_user(user_id)

        if sub and sub.plan:
            return bool(sub.plan.features.get(feature, False))

        free_plan = await repo.get_plan_by_name("FREE")
        if free_plan:
            return bool(free_plan.features.get(feature, False))

        return False
