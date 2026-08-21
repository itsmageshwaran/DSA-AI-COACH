"""Service for evaluating and unlocking achievements."""

from __future__ import annotations

from sqlalchemy import select
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.domain.learning.models import Achievement, UserAchievement, Submission

class AchievementService:
    @staticmethod
    async def evaluate_achievements(uow: UnitOfWork, user_id: str) -> list[dict]:
        """Evaluate and unlock new achievements for the user."""
        newly_unlocked = []
        
        # 1. Fetch user's existing achievements
        user_ach_result = await uow.session.execute(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        )
        existing_achievements = {ua.achievement_id for ua in user_ach_result.scalars().all()}
        
        # 2. Fetch all achievement definitions
        ach_result = await uow.session.execute(select(Achievement))
        all_achievements = list(ach_result.scalars().all())
        
        if not all_achievements:
            return [] # No achievements defined
            
        # 3. Fetch user submissions
        sub_result = await uow.session.execute(
            select(Submission).where(Submission.user_id == user_id, Submission.status == "passed")
        )
        passed_submissions = list(sub_result.scalars().all())
        passed_count = len(passed_submissions)
        
        # Evaluate specific rules
        for ach in all_achievements:
            if ach.id in existing_achievements:
                continue
                
            unlocked = False
            if ach.type == "FIRST_STEP" and passed_count >= 1:
                unlocked = True
            elif ach.type == "FIRST_5_PROBLEMS" and passed_count >= 5:
                unlocked = True
            elif ach.type == "PROBLEM_SOLVER_10" and passed_count >= 10:
                unlocked = True
            elif ach.type == "PROBLEM_SOLVER_25" and passed_count >= 25:
                unlocked = True
            elif ach.type == "PROBLEM_SOLVER_50" and passed_count >= 50:
                unlocked = True
                
            # Note: We could add more complex evaluations here (DIFFICULTY_UP, etc.)
            # by joining with Exercise difficulty.
            
            if unlocked:
                ua = UserAchievement(user_id=user_id, achievement_id=ach.id)
                uow.session.add(ua)
                newly_unlocked.append({
                    "id": ach.id,
                    "type": ach.type,
                    "title": ach.title,
                    "description": ach.description,
                    "icon": ach.icon
                })
                
        return newly_unlocked
