"""AI Application Service managing LLM completions, Socratic tutoring, and guardrails."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.ai.gateway import ai_gateway
from src.infrastructure.ai.guardrails.input_guard import input_guardrail
from src.infrastructure.ai.prompts.context_builder import prune_code_context
from src.infrastructure.ai.prompts.templates import socratic_tutor_template
from src.infrastructure.ai.schemas import LLMMessage, TaskType
from src.infrastructure.ai.telemetry import record_llm_telemetry
from src.modules.ai.schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    SocraticHintRequest,
    SocraticHintResponse,
)


class AIService:
    """Application service for AI completions and tutoring interactions."""

    async def generate_completion(
        self, user_id: str, request: AIGenerateRequest, session: AsyncSession
    ) -> AIGenerateResponse:
        """Generate completion after validating input prompt through safety guardrails."""
        from src.infrastructure.database.unit_of_work import UnitOfWork
        from src.modules.billing.entitlement_service import EntitlementService

        uow = UnitOfWork(session=session)
        entitlement_service = EntitlementService(uow)

        # Consume quota for 1 AI request
        await entitlement_service.consume_quota(
            user_id=user_id, resource="ai_requests", amount=1, metadata_info={"action": "generate_completion"}
        )

        # 1. Run Input Guardrail
        guardrail_result = input_guardrail.validate(request.prompt)
        if not guardrail_result.is_safe:
            reasons = "; ".join(guardrail_result.flagged_reasons)
            err_msg = f"Prompt safety violation: {reasons}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

        # 2. Build message context
        messages: list[LLMMessage] = []
        if request.system_prompt:
            messages.append(LLMMessage(role="system", content=request.system_prompt))
        messages.append(LLMMessage(role="user", content=guardrail_result.sanitized_prompt))

        # 3. Generate response via AI Gateway
        response = await ai_gateway.generate(
            messages=messages,
            task_type=request.task_type,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # 4. Record telemetry and consume tokens
        record_llm_telemetry(response)

        # Consume tokens quota based on usage
        if response.total_tokens > 0:
            await entitlement_service.consume_quota(
                user_id=user_id,
                resource="ai_tokens",
                amount=response.total_tokens,
                metadata_info={"action": "generate_completion"},
            )

        return AIGenerateResponse(
            response=response,
            guardrail=guardrail_result,
        )

    async def generate_socratic_hint(
        self, user_id: str, request: SocraticHintRequest, session: AsyncSession
    ) -> SocraticHintResponse:
        """Generate Socratic hint using prompt template and context pruner."""
        from src.infrastructure.database.unit_of_work import UnitOfWork
        from src.modules.billing.entitlement_service import EntitlementService

        uow = UnitOfWork(session=session)
        entitlement_service = EntitlementService(uow)

        # Consume quota for 1 AI request
        await entitlement_service.consume_quota(
            user_id=user_id, resource="ai_requests", amount=1, metadata_info={"action": "generate_socratic_hint"}
        )

        # Prune long code context
        pruned_code = prune_code_context(request.code, max_tokens=600)

        # Build Socratic prompt messages
        messages = socratic_tutor_template.format_messages(
            exercise_title=request.exercise_title,
            concept_name=request.concept_name,
            code=pruned_code,
            execution_output=request.execution_output,
            user_query=request.user_query,
        )

        response = await ai_gateway.generate(
            messages=messages,
            task_type=TaskType.SOCRATIC_TUTOR,
            temperature=0.6,
            max_tokens=500,
        )

        record_llm_telemetry(response)

        # Consume tokens quota
        if response.total_tokens > 0:
            await entitlement_service.consume_quota(
                user_id=user_id,
                resource="ai_tokens",
                amount=response.total_tokens,
                metadata_info={"action": "generate_socratic_hint"},
            )

        return SocraticHintResponse(
            hint=response.content,
            task_type=TaskType.SOCRATIC_TUTOR,
            llm_response=response,
        )

    async def generate_stream(
        self, user_id: str, request: AIGenerateRequest, session: AsyncSession
    ) -> AsyncGenerator[str, None]:
        """Stream token generator for AI completion."""
        from src.infrastructure.database.unit_of_work import UnitOfWork
        from src.modules.billing.entitlement_service import EntitlementService

        uow = UnitOfWork(session=session)
        entitlement_service = EntitlementService(uow)

        # Consume quota for 1 AI request
        await entitlement_service.consume_quota(
            user_id=user_id, resource="ai_requests", amount=1, metadata_info={"action": "generate_stream"}
        )

        guardrail_result = input_guardrail.validate(request.prompt)
        if not guardrail_result.is_safe:
            reasons = "; ".join(guardrail_result.flagged_reasons)
            err_msg = f"Prompt safety violation: {reasons}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

        messages: list[LLMMessage] = []
        if request.system_prompt:
            messages.append(LLMMessage(role="system", content=request.system_prompt))
        messages.append(LLMMessage(role="user", content=guardrail_result.sanitized_prompt))

        # Currently streaming responses don't return usage directly easily in our generic gateway,
        # but we could consume tokens incrementally or estimate.
        # For this implementation, we will rely strictly on the `ai_requests` limit above for streaming
        # to avoid blocking the generator.

        async for chunk in ai_gateway.generate_stream(
            messages=messages,
            task_type=request.task_type,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ):
            yield chunk


ai_service = AIService()
