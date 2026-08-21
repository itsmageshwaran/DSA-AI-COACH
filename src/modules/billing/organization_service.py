"""Enterprise Organization Tenancy and Role Service."""

from __future__ import annotations

from typing import Any
from collections.abc import Sequence

from fastapi import HTTPException, status

from src.infrastructure.database.unit_of_work import UnitOfWork
from src.repositories.billing_repository import BillingRepository
from src.domain.billing.models import Organization, OrganizationMember, AuditLog


class OrganizationService:
    """Service for managing enterprise tenancy and membership."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_user_organizations(self, user_id: str) -> Sequence[Organization]:
        """Get organizations a user is a member of."""
        repo = BillingRepository(self.uow.session)
        return await repo.get_user_organizations(user_id)

    async def verify_membership(
        self, user_id: str, organization_id: str, required_roles: list[str] | None = None
    ) -> bool:
        """Verify user is an active member of the organization and has required roles."""
        repo = BillingRepository(self.uow.session)
        orgs = await repo.get_user_organizations(user_id)

        # We manually fetch the specific membership role here.
        # Alternatively, the repo could fetch members directly.
        from sqlalchemy import select

        stmt = (
            select(OrganizationMember)
            .join(Organization)
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id,
                Organization.is_active == True,
            )
        )
        result = await self.uow.session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            return False

        if required_roles and member.role not in required_roles:
            return False

        return True

    async def require_organization_access(
        self, user_id: str, organization_id: str, required_roles: list[str] | None = None
    ) -> None:
        """Raise 403 if user lacks access to the organization. Prevents IDOR."""
        has_access = await self.verify_membership(user_id, organization_id, required_roles)
        if not has_access:
            # Audit log the failed authorization attempt
            self.log_audit_event(
                actor_id=user_id,
                action="organization_access_denied",
                resource=f"organization:{organization_id}",
                organization_id=organization_id,
                metadata_info={"required_roles": required_roles},
            )
            await self.uow.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this organization or lack the required role.",
            )

    def log_audit_event(
        self,
        actor_id: str | None,
        action: str,
        resource: str | None = None,
        organization_id: str | None = None,
        request_id: str | None = None,
        metadata_info: dict[str, Any] | None = None,
    ) -> None:
        """Create an immutable audit log record. (Implementation of PHASE 6 - Audit Logging)"""
        repo = BillingRepository(self.uow.session)
        audit_log = AuditLog(
            actor_id=actor_id,
            action=action,
            resource=resource,
            organization_id=organization_id,
            request_id=request_id,
            metadata_info=metadata_info or {},
        )
        repo.add_audit_log(audit_log)
