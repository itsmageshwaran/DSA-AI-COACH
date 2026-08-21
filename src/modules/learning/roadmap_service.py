"""Service for Personalized Career Roadmaps."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.domain.auth.models import UserProfile
from src.domain.learning.models import Concept, Lesson, Exercise, Progress

ROADMAP_TEMPLATES = {
    "Backend Engineering": [
        "Arrays",
        "Strings",
        "Stack",
        "Linked Lists",
        "Sorting",
        "Binary Search",
        "Two Pointers",
        "Sliding Window",
        "Greedy",
        "Graph Traversal",
        "Graph Algorithms",
        "Backtracking",
        "Dynamic Programming",
        "Advanced DP"
    ],
    "Frontend Engineering": [
        "Strings",
        "Arrays",
        "Two Pointers",
        "Sliding Window",
        "Stack",
        "Linked Lists",
        "Sorting",
        "Greedy",
        "Binary Search",
        "Graph Traversal",
        "Dynamic Programming",
        "Backtracking",
        "Graph Algorithms",
        "Advanced DP"
    ],
    "Full Stack Engineering": [
        "Arrays",
        "Strings",
        "Two Pointers",
        "Stack",
        "Linked Lists",
        "Sliding Window",
        "Sorting",
        "Binary Search",
        "Greedy",
        "Graph Traversal",
        "Backtracking",
        "Dynamic Programming",
        "Graph Algorithms",
        "Advanced DP"
    ],
    "Data Science": [
        "Arrays",
        "Strings",
        "Sorting",
        "Two Pointers",
        "Binary Search",
        "Greedy",
        "Dynamic Programming",
        "Graph Traversal",
        "Stack",
        "Linked Lists",
        "Sliding Window",
        "Backtracking",
        "Graph Algorithms",
        "Advanced DP"
    ],
    "Machine Learning / AI": [
        "Arrays",
        "Sorting",
        "Binary Search",
        "Greedy",
        "Dynamic Programming",
        "Advanced DP",
        "Graph Traversal",
        "Graph Algorithms",
        "Strings",
        "Two Pointers",
        "Backtracking",
        "Stack",
        "Linked Lists",
        "Sliding Window"
    ],
    "Cybersecurity": [
        "Strings",
        "Arrays",
        "Two Pointers",
        "Sorting",
        "Stack",
        "Linked Lists",
        "Graph Traversal",
        "Graph Algorithms",
        "Binary Search",
        "Greedy",
        "Backtracking",
        "Dynamic Programming",
        "Sliding Window",
        "Advanced DP"
    ],
}

DEFAULT_ROADMAP = ROADMAP_TEMPLATES["Backend Engineering"]

class RoadmapService:
    @staticmethod
    async def generate_roadmap(uow: UnitOfWork, user_id: str) -> dict:
        """Generate a personalized roadmap based on user profile and progress."""
        
        # 1. Fetch User Profile
        result = await uow.session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profile = result.scalar_one_or_none()
        
        career_goal = profile.career_goal if profile else None
        template = ROADMAP_TEMPLATES.get(career_goal, DEFAULT_ROADMAP) if career_goal else DEFAULT_ROADMAP
        
        # 2. Fetch Concepts matching template
        concept_result = await uow.session.execute(select(Concept))
        all_concepts = list(concept_result.scalars().all())
        concept_map = {c.name.lower(): c for c in all_concepts}
        
        # 3. Fetch user progress
        prog_result = await uow.session.execute(select(Progress).where(Progress.user_id == user_id))
        user_progress = list(prog_result.scalars().all())
        completed_lesson_ids = {p.lesson_id for p in user_progress if p.completed}
        
        # 4. Fetch all lessons and exercises mapping to concepts
        lesson_result = await uow.session.execute(
            select(Lesson).options(joinedload(Lesson.exercises))
        )
        all_lessons = list(lesson_result.unique().scalars().all())
        
        concept_to_lessons = {}
        for lesson in all_lessons:
            if lesson.concept_id not in concept_to_lessons:
                concept_to_lessons[lesson.concept_id] = []
            concept_to_lessons[lesson.concept_id].append(lesson)
            
        # 5. Build Roadmap phases
        phases = []
        is_locked = False
        current_found = False
        
        for phase_name in template:
            # Match concept
            concept = concept_map.get(phase_name.lower())
            
            phase = {
                "name": phase_name,
                "concept_id": concept.id if concept else None,
                "status": "LOCKED",
                "completed_lessons": 0,
                "total_lessons": 0,
                "description": concept.description if concept else f"Master {phase_name}"
            }
            
            if concept and concept.id in concept_to_lessons:
                lessons = concept_to_lessons[concept.id]
                phase["total_lessons"] = len(lessons)
                phase["completed_lessons"] = sum(1 for l in lessons if l.id in completed_lesson_ids)
            
            if is_locked:
                phase["status"] = "LOCKED"
            else:
                if phase["total_lessons"] > 0 and phase["completed_lessons"] >= phase["total_lessons"]:
                    phase["status"] = "COMPLETED"
                else:
                    if not current_found:
                        phase["status"] = "CURRENT"
                        current_found = True
                        # If strict sequence, lock subsequent
                        is_locked = True
                    else:
                        phase["status"] = "LOCKED"
                        
            phases.append(phase)
            
        return {
            "career_goal": career_goal or "General Software Engineering",
            "phases": phases,
            "overall_progress": sum(p["completed_lessons"] for p in phases) / max(1, sum(p["total_lessons"] for p in phases)) * 100 if sum(p["total_lessons"] for p in phases) > 0 else 0
        }

