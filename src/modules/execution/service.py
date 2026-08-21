"""Execution application service orchestrating code execution, submissions, and progress tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status
from src.domain.learning.models import Exercise, Progress, Submission
from src.infrastructure.execution.engine import execution_engine
from src.infrastructure.execution.schemas import (
    ExecutionStatus,
    TestCaseInput,
)
from src.modules.execution.schemas import (
    ExecutionRunRequest,
    ExecutionRunResponse,
    ExecutionSubmitRequest,
    ExecutionSubmitResponse,
)


class ExecutionService:
    """Service handling code execution runs and submission evaluation."""

    async def run_code(self, user_id: str, request: ExecutionRunRequest, session: AsyncSession) -> ExecutionRunResponse:
        """Run source code against provided test cases without persisting submission."""
        from src.infrastructure.database.unit_of_work import UnitOfWork
        from src.modules.billing.entitlement_service import EntitlementService

        uow = UnitOfWork(session=session)
        entitlement_service = EntitlementService(uow)

        # Consume code execution quota
        await entitlement_service.consume_quota(
            user_id=user_id, resource="code_executions", amount=1, metadata_info={"action": "run_code"}
        )

        result = await execution_engine.run_code(
            code=request.code,
            language=request.language,
            test_cases=request.test_cases,
            entrypoint=request.entrypoint,
        )
        return ExecutionRunResponse(execution=result)

    async def submit_code(
        self,
        user_id: str,
        request: ExecutionSubmitRequest,
        session: AsyncSession,
    ) -> ExecutionSubmitResponse:
        """Evaluate exercise code submission, record Submission, and update Progress if accepted."""
        from src.infrastructure.database.unit_of_work import UnitOfWork
        from src.modules.billing.entitlement_service import EntitlementService

        uow = UnitOfWork(session=session)
        entitlement_service = EntitlementService(uow)

        # Consume code execution quota
        await entitlement_service.consume_quota(
            user_id=user_id,
            resource="code_executions",
            amount=1,
            metadata_info={"action": "submit_code", "exercise_id": request.exercise_id},
        )

        stmt = select(Exercise).where(Exercise.id == request.exercise_id)
        result = await session.execute(stmt)
        exercise = result.scalar_one_or_none()

        if not exercise:
            err_msg = f"Exercise '{request.exercise_id}' not found."
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)

        test_cases = request.custom_test_cases or self._extract_test_cases_from_exercise(exercise)

        exec_result = await execution_engine.run_code(
            code=request.code,
            language=request.language,
            test_cases=test_cases,
            entrypoint=request.entrypoint,
        )

        submission_status = exec_result.status.value.lower()
        passed_ratio = round(exec_result.pass_rate * 100, 1)
        feedback_msg = (
            f"Passed {exec_result.passed_count}/{exec_result.total_count} test cases. Pass rate: {passed_ratio}%."
        )

        submission = Submission(
            user_id=user_id,
            exercise_id=request.exercise_id,
            code=request.code,
            status=submission_status,
            feedback=feedback_msg,
        )
        session.add(submission)
        
        new_achievements = []
        progress_updated = False
        mastery_update = None
        next_problem = None
        
        if exec_result.status == ExecutionStatus.ACCEPTED:
            from src.modules.learning.service import get_concept_mastery
            # Pre-mastery
            old_mastery = await get_concept_mastery(uow, user_id)
            old_mastery_dict = {m.concept_name: m.mastery_percentage for m in old_mastery}

            progress_updated = await self._update_lesson_progress(
                user_id=user_id,
                lesson_id=exercise.lesson_id,
                score=100.0,
                session=session,
            )
            from src.modules.learning.achievement_service import AchievementService
            new_achievements = await AchievementService.evaluate_achievements(uow, user_id)
            
            # Post-mastery
            new_mastery = await get_concept_mastery(uow, user_id)
            new_mastery_dict = {m.concept_name: m.mastery_percentage for m in new_mastery}
            
            # Find the concept that changed
            for concept, new_pct in new_mastery_dict.items():
                old_pct = old_mastery_dict.get(concept, 0)
                if new_pct > old_pct:
                    mastery_update = {
                        "concept": concept,
                        "old_percentage": old_pct,
                        "new_percentage": new_pct
                    }
                    break

        # Calculate next problem for ANY submission, to update difficulty if failed
        from src.modules.learning.recommendation_service import RecommendationService
        next_problem = await RecommendationService.get_next_problem(uow, user_id)

        await session.commit()
        await session.refresh(submission)

        return ExecutionSubmitResponse(
            submission_id=submission.id,
            exercise_id=exercise.id,
            status=submission_status,
            execution=exec_result,
            progress_updated=progress_updated,
            new_achievements=new_achievements,
            mastery_update=mastery_update,
            next_problem=next_problem
        )

    def _extract_test_cases_from_exercise(self, exercise: Exercise) -> list[TestCaseInput]:
        """Generate test cases from exercise specifications or default fallback."""
        if hasattr(exercise, 'test_cases_json') and exercise.test_cases_json:
            return [
                TestCaseInput(
                    input_data=tc.get("input"),
                    expected_output=tc.get("expected"),
                    is_hidden=tc.get("is_hidden", False)
                ) for tc in exercise.test_cases_json
            ]
        return [
            TestCaseInput(input_data=[1, 2], expected_output=3, is_hidden=False),
        ]

    async def _update_lesson_progress(
        self,
        user_id: str,
        lesson_id: str,
        score: float,
        session: AsyncSession,
    ) -> bool:
        """Update or create Progress record when submission is accepted."""
        stmt = select(Progress).where(
            Progress.user_id == user_id,
            Progress.lesson_id == lesson_id,
        )
        res = await session.execute(stmt)
        progress = res.scalar_one_or_none()

        if not progress:
            progress = Progress(
                user_id=user_id,
                lesson_id=lesson_id,
                completed=True,
                score=score,
                completed_at=datetime.now(timezone.utc),
            )
            session.add(progress)
            return True

        progress.completed = True
        progress.score = max(progress.score or 0.0, score)
        progress.completed_at = datetime.now(timezone.utc)
        return True


execution_service = ExecutionService()

