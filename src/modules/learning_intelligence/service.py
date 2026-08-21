from datetime import datetime, timedelta, timezone
import math
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.repositories.learning_intelligence_repository import LearningIntelligenceRepository
from src.domain.learning_intelligence.models import ConceptReviewState, ReviewLog, SkillMastery
from sqlalchemy import select


class SuperMemo2Engine:
    """Deterministic implementation of the SuperMemo-2 algorithm.
    Used to calculate intervals for spaced repetition.
    """

    @staticmethod
    def calculate_next_review(
        grade: int, easiness_factor: float = 2.5, interval: int = 0, repetitions: int = 0
    ) -> tuple[int, int, float]:
        """Calculates the next interval, repetition count, and easiness factor.

        Args:
            grade: Score from 0 (complete blackout) to 5 (perfect response)
            easiness_factor: Current easiness factor (default 2.5 for new items)
            interval: Current interval in days
            repetitions: Current number of consecutive correct repetitions

        Returns:
            Tuple of (new_interval, new_repetitions, new_easiness_factor)

        """
        if grade < 0 or grade > 5:
            raise ValueError("Grade must be between 0 and 5.")

        if grade >= 3:
            # Correct response
            if repetitions == 0:
                new_interval = 1
            elif repetitions == 1:
                new_interval = 6
            else:
                new_interval = math.ceil(interval * easiness_factor)
            new_repetitions = repetitions + 1
        else:
            # Incorrect response
            new_repetitions = 0
            new_interval = 1

        # Calculate new easiness factor
        new_easiness_factor = easiness_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))

        # Easiness factor must never drop below 1.3
        new_easiness_factor = max(1.3, new_easiness_factor)

        return new_interval, new_repetitions, new_easiness_factor


class MasteryCalculator:
    """Deterministic engine for calculating overall skill mastery and decay over time."""

    @staticmethod
    def calculate_mastery(
        successful_reviews: int,
        total_reviews: int,
        average_easiness: float,
        last_review_date: datetime,
        current_date: datetime,
    ) -> float:
        """Calculates a mastery percentage [0.0 - 100.0] based on review history and time decay."""
        if total_reviews == 0:
            return 0.0

        # Base accuracy
        accuracy = successful_reviews / total_reviews

        # Factor in how easy it was (1.3 is hardest, 2.5 is average/baseline)
        easiness_weight = min(1.0, average_easiness / 2.5)

        # Calculate raw mastery
        raw_mastery = accuracy * easiness_weight * 100.0

        # Calculate time decay (Ebbinghaus inspired but deterministic)
        days_since_review = max(0, (current_date - last_review_date).days)

        # Decay slows down as mastery increases (easiness factor acts as a shield)
        decay_rate = 0.05 / max(1.0, average_easiness)
        decay_amount = raw_mastery * (1.0 - math.exp(-decay_rate * days_since_review))

        # Apply decay but keep it within bounds
        final_mastery = max(0.0, min(100.0, raw_mastery - decay_amount))

        return round(final_mastery, 2)


class LearningIntelligenceService:
    @staticmethod
    async def record_concept_review(uow: UnitOfWork, user_id: str, concept_id: str, grade: int) -> ConceptReviewState:
        """Record a concept review and calculate the next review date using SM-2 algorithm.

        Args:
            uow: The unit of work.
            user_id: The ID of the user.
            concept_id: The ID of the concept.
            grade: The grade (0-5) of the review.

        Returns:
            The updated ConceptReviewState.
        """
        if grade < 0 or grade > 5:
            msg = "Grade must be between 0 and 5"
            raise ValueError(msg)

        repo = LearningIntelligenceRepository(uow.session)
        state = await repo.get_concept_review_state(user_id, concept_id)
        now = datetime.now(timezone.utc)

        if not state:
            state = ConceptReviewState(
                user_id=user_id,
                concept_id=concept_id,
                ease_factor=2.5,
                interval_days=0,
                repetitions=0,
                next_review_date=now,
            )
            state = await repo.create_concept_review_state(state)

        new_interval, new_reps, new_ease = SuperMemo2Engine.calculate_next_review(
            grade=grade, easiness_factor=state.ease_factor, interval=state.interval_days, repetitions=state.repetitions
        )

        state.interval_days = new_interval
        state.repetitions = new_reps
        state.ease_factor = new_ease
        state.last_reviewed_at = now
        state.next_review_date = now + timedelta(days=new_interval)

        await repo.update_concept_review_state(state)

        review_log = ReviewLog(user_id=user_id, concept_id=concept_id, quality=grade, reviewed_at=now)
        await repo.log_review(review_log)

        await uow.commit()
        return state

    @staticmethod
    async def get_due_reviews(uow: UnitOfWork, user_id: str) -> list[ConceptReviewState]:
        """Get all due concept reviews for a user.

        Args:
            uow: The unit of work.
            user_id: The ID of the user.

        Returns:
            A list of due ConceptReviewState objects.
        """
        stmt = select(ConceptReviewState).where(
            ConceptReviewState.user_id == user_id, ConceptReviewState.next_review_date <= datetime.now(timezone.utc)
        )
        result = await uow.session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_skill_mastery(uow: UnitOfWork, user_id: str, skill_id: str) -> SkillMastery:
        """Update mastery level for a specific skill based on recent performance.

        Args:
            uow: The unit of work.
            user_id: The ID of the user.
            skill_id: The ID of the skill.

        Returns:
            The updated SkillMastery.
        """
        repo = LearningIntelligenceRepository(uow.session)

        # To calculate skill mastery, we aggregate review states for concepts related to this skill
        # A skill is related to concepts via Lessons (Lesson has skill_id and concept_id)
        # So we find all concepts for this skill
        from src.domain.learning.models import Lesson

        stmt = select(Lesson.concept_id).where(Lesson.skill_id == skill_id, Lesson.concept_id.isnot(None)).distinct()

        result = await uow.session.execute(stmt)
        concept_ids = list(result.scalars().all())

        if not concept_ids:
            # If a skill has no concepts mapped, we just initialize it as 0 mastery
            mastery = await repo.get_skill_mastery(user_id, skill_id)
            if not mastery:
                mastery = await repo.create_skill_mastery(
                    SkillMastery(user_id=user_id, skill_id=skill_id, mastery_level=0.0)
                )
                await uow.commit()
            return mastery

        # Get review states for these concepts
        stmt_states = select(ConceptReviewState).where(
            ConceptReviewState.user_id == user_id, ConceptReviewState.concept_id.in_(concept_ids)
        )
        result_states = await uow.session.execute(stmt_states)
        states = list(result_states.scalars().all())

        # We need historical review logs to calculate total and successful reviews
        stmt_logs = select(ReviewLog).where(ReviewLog.user_id == user_id, ReviewLog.concept_id.in_(concept_ids))
        result_logs = await uow.session.execute(stmt_logs)
        logs = list(result_logs.scalars().all())

        total_reviews = len(logs)
        successful_reviews = sum(1 for log in logs if log.quality >= 3)

        if len(states) > 0:
            avg_easiness = sum(state.ease_factor for state in states) / len(states)
            # Find the most recent review among these concepts
            last_review_dates = [state.last_reviewed_at for state in states if state.last_reviewed_at]
            last_review_date = max(last_review_dates) if last_review_dates else datetime.now(timezone.utc)
        else:
            avg_easiness = 2.5
            last_review_date = datetime.now(timezone.utc)

        mastery_percentage = MasteryCalculator.calculate_mastery(
            successful_reviews=successful_reviews,
            total_reviews=total_reviews,
            average_easiness=avg_easiness,
            last_review_date=last_review_date,
            current_date=datetime.now(timezone.utc),
        )

        mastery = await repo.get_skill_mastery(user_id, skill_id)
        now = datetime.now(timezone.utc)
        if not mastery:
            mastery = SkillMastery(
                user_id=user_id, skill_id=skill_id, mastery_level=mastery_percentage, last_activity_at=now
            )
            mastery = await repo.create_skill_mastery(mastery)
        else:
            mastery.mastery_level = mastery_percentage
            mastery.last_activity_at = now
            await repo.update_skill_mastery(mastery)

        await uow.commit()
        return mastery

    @staticmethod
    async def get_recommendations(uow: UnitOfWork, user_id: str, limit: int = 5) -> list[str]:
        """Get concept recommendations for the user based on due reviews.

        Args:
            uow: The unit of work.
            user_id: The ID of the user.
            limit: Maximum number of recommendations to return.

        Returns:
            A list of recommended concept IDs.
        """
        # Return due concept IDs, ordered by interval (most overdue/shortest interval first)
        stmt = (
            select(ConceptReviewState.concept_id)
            .where(
                ConceptReviewState.user_id == user_id, ConceptReviewState.next_review_date <= datetime.now(timezone.utc)
            )
            .order_by(ConceptReviewState.interval_days.asc())
            .limit(limit)
        )

        result = await uow.session.execute(stmt)
        return list(result.scalars().all())
