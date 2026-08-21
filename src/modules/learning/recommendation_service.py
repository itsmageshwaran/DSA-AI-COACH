"""Service for Next Best Problem Recommendation and Difficulty Progression."""

from __future__ import annotations

import random
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.domain.auth.models import UserProfile
from src.domain.learning.models import Concept, Lesson, Exercise, Progress, Submission
from src.modules.learning.roadmap_service import RoadmapService

DIFFICULTY_LEVELS = ["easy", "easy+", "medium", "medium+", "hard", "advanced"]

class RecommendationService:
    @staticmethod
    async def get_next_problem(uow: UnitOfWork, user_id: str) -> dict:
        """Determine the next best problem based on roadmap and difficulty progression."""
        
        # 1. Get user roadmap phase
        roadmap_data = await RoadmapService.generate_roadmap(uow, user_id)
        current_phase = next((p for p in roadmap_data["phases"] if p["status"] == "CURRENT"), None)
        
        if not current_phase:
            # If all completed, return a random revision or empty
            return {
                "exercise_id": None,
                "title": "All Caught Up!",
                "difficulty": "N/A",
                "concept": "Mastery",
                "roadmap_phase": "Complete",
                "reason": "You have completed your personalized roadmap."
            }
            
        concept_id = current_phase.get("concept_id")
        concept_name = current_phase.get("name")
        
        # 2. Get user submissions for this concept to determine difficulty
        # We need all exercises for this concept
        lesson_result = await uow.session.execute(
            select(Lesson).options(joinedload(Lesson.exercises)).where(Lesson.concept_id == concept_id)
        )
        lessons = list(lesson_result.unique().scalars().all())
        
        exercise_ids = [ex.id for lesson in lessons for ex in lesson.exercises]
        
        sub_result = await uow.session.execute(
            select(Submission).where(Submission.user_id == user_id, Submission.exercise_id.in_(exercise_ids))
        )
        submissions = list(sub_result.scalars().all())
        
        # Calculate mastery/difficulty state
        # A simple deterministic rule: 
        # Start at "easy".
        # 2 successful "easy" -> unlock "easy+". 
        # 2 successful "easy+" -> unlock "medium", etc.
        
        passed_by_diff = {d: 0 for d in DIFFICULTY_LEVELS}
        failed_by_diff = {d: 0 for d in DIFFICULTY_LEVELS}
        
        # Group submissions by exercise to only count distinct successful exercises
        exercise_status = {}
        for sub in submissions:
            ex_diff = next((ex.difficulty for lesson in lessons for ex in lesson.exercises if ex.id == sub.exercise_id), "easy")
            if sub.exercise_id not in exercise_status or exercise_status[sub.exercise_id] != "passed":
                exercise_status[sub.exercise_id] = sub.status
                
        for eid, status in exercise_status.items():
            ex_diff = next((ex.difficulty for lesson in lessons for ex in lesson.exercises if ex.id == eid), "easy")
            if status == "passed":
                passed_by_diff[ex_diff] += 1
            else:
                failed_by_diff[ex_diff] += 1
                
        target_diff_index = 0
        for i, diff in enumerate(DIFFICULTY_LEVELS):
            if passed_by_diff[diff] >= 2:
                target_diff_index = min(len(DIFFICULTY_LEVELS) - 1, i + 1)
                
        # Handle failure downgrade recommendation
        # If they failed the target difficulty 3 times, recommend a revision at lower difficulty
        target_diff = DIFFICULTY_LEVELS[target_diff_index]
        is_revision = False
        if failed_by_diff[target_diff] >= 3 and target_diff_index > 0:
            target_diff_index -= 1
            target_diff = DIFFICULTY_LEVELS[target_diff_index]
            is_revision = True
            
        # 3. Find an uncompleted exercise at target difficulty
        candidate_exercises = []
        for lesson in lessons:
            for ex in lesson.exercises:
                if ex.difficulty == target_diff and exercise_status.get(ex.id) != "passed":
                    candidate_exercises.append(ex)
                    
        # If no exercise found at target, try next difficulty, or just return first available
        if not candidate_exercises:
            for lesson in lessons:
                for ex in lesson.exercises:
                    if exercise_status.get(ex.id) != "passed":
                        candidate_exercises.append(ex)
                        
        if candidate_exercises:
            next_ex = candidate_exercises[0]
            reason = f"You're currently focusing on {concept_name}."
            if is_revision:
                reason = f"You struggled with the previous {DIFFICULTY_LEVELS[target_diff_index+1].title()} problem. Strengthen the concept with a {target_diff.title()} revision problem."
            elif target_diff_index > 0 and passed_by_diff[DIFFICULTY_LEVELS[target_diff_index-1]] >= 2:
                reason = f"You've demonstrated enough mastery in {DIFFICULTY_LEVELS[target_diff_index-1].title()} problems to begin {target_diff.title()}."
            
            return {
                "exercise_id": next_ex.id,
                "title": next_ex.title,
                "difficulty": next_ex.difficulty,
                "concept": concept_name,
                "roadmap_phase": concept_name,
                "reason": reason
            }
            
        # If all exercises in concept are passed, they should progress to next concept
        return {
            "exercise_id": None,
            "title": "Phase Complete",
            "difficulty": "N/A",
            "concept": concept_name,
            "roadmap_phase": concept_name,
            "reason": "You've mastered this concept. Check your roadmap for the next step."
        }
