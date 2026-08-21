"""FastAPI Router for Billing, Subscription, and Organization endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import User
from src.infrastructure.database.dependencies import get_db_session
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.modules.auth.dependencies import get_current_active_user
from src.modules.billing.entitlement_service import EntitlementService
from src.modules.billing.organization_service import OrganizationService

router = APIRouter()


class QuotaResponse(BaseModel):
    limits: dict[str, int]
    # We could optionally include current usage here if we fetch it from Redis


class ChangePlanRequest(BaseModel):
    plan_id: str


@router.get(
    "/quota",
    name="billing-quota",
    response_model=QuotaResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_quota(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> QuotaResponse:
    """Get the current user's daily limits."""
    uow = UnitOfWork(session=db)
    entitlement_service = EntitlementService(uow)
    limits = await entitlement_service.resolve_limits(current_user.id)
    return QuotaResponse(limits=limits)


@router.get(
    "/organizations",
    name="billing-organizations",
    status_code=status.HTTP_200_OK,
)
async def list_user_organizations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[dict[str, Any]]:
    """List organizations the user belongs to."""
    uow = UnitOfWork(session=db)
    org_service = OrganizationService(uow)
    orgs = await org_service.get_user_organizations(current_user.id)

    return [
        {
            "id": org.id,
            "name": org.name,
            "tier": org.subscription.plan.name if org.subscription and org.subscription.plan else "free",
        }
        for org in orgs
    ]


@router.post(
    "/webhook",
    name="billing-webhook",
    status_code=status.HTTP_200_OK,
)
async def billing_webhook(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Receive webhooks from the billing provider."""
    # Would validate via provider
    return {"status": "received"}
