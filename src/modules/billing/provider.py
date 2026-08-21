"""Provider-agnostic Billing Abstraction."""

from __future__ import annotations

from typing import Any, Protocol

from src.core.logging.logger import logger


class BillingProvider(Protocol):
    """Protocol defining required billing provider capabilities."""

    async def create_customer(self, user_id: str, email: str, name: str | None = None) -> str:
        """Create a customer in the provider and return provider customer ID."""
        ...

    async def create_subscription(self, customer_id: str, plan_id: str) -> str:
        """Create a subscription for a customer and return provider subscription ID."""
        ...

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel an active subscription."""
        ...

    async def change_plan(self, subscription_id: str, new_plan_id: str) -> bool:
        """Change the plan for an active subscription."""
        ...

    async def process_webhook(self, payload: dict[str, Any], signature: str) -> dict[str, Any]:
        """Validate and process a webhook from the billing provider."""
        ...


class MockBillingProvider:
    """Mock implementation of the BillingProvider for testing and local development."""

    async def create_customer(self, user_id: str, email: str, name: str | None = None) -> str:
        logger.info("MockBillingProvider: Creating customer", user_id=user_id, email=email)
        return f"cus_mock_{user_id[:8]}"

    async def create_subscription(self, customer_id: str, plan_id: str) -> str:
        logger.info("MockBillingProvider: Creating subscription", customer_id=customer_id, plan_id=plan_id)
        return f"sub_mock_{customer_id[:8]}_{plan_id[:8]}"

    async def cancel_subscription(self, subscription_id: str) -> bool:
        logger.info("MockBillingProvider: Canceling subscription", subscription_id=subscription_id)
        return True

    async def change_plan(self, subscription_id: str, new_plan_id: str) -> bool:
        logger.info("MockBillingProvider: Changing plan", subscription_id=subscription_id, new_plan_id=new_plan_id)
        return True

    async def process_webhook(self, payload: dict[str, Any], signature: str) -> dict[str, Any]:
        logger.info("MockBillingProvider: Processing webhook", payload=payload, signature=signature)
        if signature != "mock_valid_signature":
            raise ValueError("Invalid webhook signature")
        return {"status": "success", "event_type": payload.get("type", "unknown")}
