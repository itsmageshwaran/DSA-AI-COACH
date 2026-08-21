from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.learning_intelligence.models import ConceptReviewState, SkillMastery, ReviewLog


class LearningIntelligenceRepository:
    """Repository for learning intelligence models."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_concept_review_state(self, user_id: str, concept_id: str) -> ConceptReviewState | None:
        """Get the review state for a specific concept."""
        stmt = select(ConceptReviewState).where(
            ConceptReviewState.user_id == user_id, ConceptReviewState.concept_id == concept_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_concept_review_state(self, state: ConceptReviewState) -> ConceptReviewState:
        """Create a new concept review state."""
        self._session.add(state)
        await self._session.flush()
        return state

    async def update_concept_review_state(self, state: ConceptReviewState) -> ConceptReviewState:
        """Update an existing concept review state."""
        # Changes are tracked by the SQLAlchemy session
        await self._session.flush()
        return state

    async def get_skill_mastery(self, user_id: str, skill_id: str) -> SkillMastery | None:
        """Get the mastery level for a specific skill."""
        stmt = select(SkillMastery).where(SkillMastery.user_id == user_id, SkillMastery.skill_id == skill_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_skill_mastery(self, mastery: SkillMastery) -> SkillMastery:
        """Create a new skill mastery record."""
        self._session.add(mastery)
        await self._session.flush()
        return mastery

    async def update_skill_mastery(self, mastery: SkillMastery) -> SkillMastery:
        """Update an existing skill mastery record."""
        # Changes are tracked by the SQLAlchemy session
        await self._session.flush()
        return mastery

    async def log_review(self, review_log: ReviewLog) -> ReviewLog:
        """Log a review event."""
        self._session.add(review_log)
        await self._session.flush()
        return review_log
