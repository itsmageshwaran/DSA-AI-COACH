import asyncio
import sys
import json
import os
from sqlalchemy import select

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.database.session import AsyncSessionFactory
from src.domain.auth.models import User, UserProfile
from src.domain.learning.models import (
    LearningPath,
    Course,
    Module,
    Lesson,
    Exercise,
    Concept,
    Skill,
    Achievement
)

async def seed_data():
    async with AsyncSessionFactory() as session:
        # Idempotency check
        result = await session.execute(select(LearningPath).where(LearningPath.title == "DSA Mastery"))
        if result.scalars().first():
            print("Data already seeded. To re-seed, drop database or tables first.")
            return

        with open('seed_data.json', 'r') as f:
            problems = json.load(f)

        # 1. Create Concepts and Skills dynamically
        concepts_map = {}
        skills_map = {}

        for p in problems:
            if p["concept"] not in concepts_map:
                concepts_map[p["concept"]] = Concept(name=p["concept"], description=f"Master {p['concept']}")
                session.add(concepts_map[p["concept"]])
            if p["skill"] not in skills_map:
                skills_map[p["skill"]] = Skill(name=p["skill"], description=f"Applying {p['skill']}")
                session.add(skills_map[p["skill"]])
        
        await session.flush()

        # 2. Create Learning Paths
        path = LearningPath(
            title="DSA Mastery",
            description="Master Data Structures and Algorithms from scratch.",
            is_published=True
        )
        session.add(path)
        await session.flush()

        # 3. Create Courses (Group concepts logically)
        course = Course(
            title="Complete DSA Bootcamp",
            description="A comprehensive guide to all algorithms and data structures.",
            learning_path_id=path.id
        )
        session.add(course)
        await session.flush()

        # 4. Create Modules (Group by difficulty or topic)
        module_easy = Module(title="Foundations (Easy)", description="Start here", order=1, course_id=course.id)
        module_medium = Module(title="Core Algorithms (Medium)", description="Intermediate", order=2, course_id=course.id)
        module_hard = Module(title="Advanced (Hard)", description="Mastery", order=3, course_id=course.id)
        
        session.add_all([module_easy, module_medium, module_hard])
        await session.flush()

        # 5. Create Lessons & Exercises
        for idx, p in enumerate(problems, 1):
            # Assign module based on difficulty
            mod_id = module_easy.id
            if "Medium" in p["difficulty"]:
                mod_id = module_medium.id
            elif "Hard" in p["difficulty"] or "Advanced" in p["difficulty"]:
                mod_id = module_hard.id
            
            lesson = Lesson(
                title=p["title"],
                content=f"Learn about {p['title']} using {p['skill']}.",
                order=idx,
                module_id=mod_id,
                concept_id=concepts_map[p["concept"]].id,
                skill_id=skills_map[p["skill"]].id
            )
            session.add(lesson)
            await session.flush()

            exercise = Exercise(
                title=p["title"],
                instructions=p["instructions"],
                starter_code=p["starter_code"],
                test_cases_json=p["test_cases"],
                entrypoint=p["entrypoint"],
                difficulty=p["difficulty"].lower().replace("+", "_plus"),
                lesson_id=lesson.id
            )
            session.add(exercise)
            await session.flush()

        # 6. Create Achievements
        achievements = [
            Achievement(type="FIRST_STEP", title="First Step", description="Solved your first problem.", icon="Star"),
            Achievement(type="FIRST_5_PROBLEMS", title="Getting Warmed Up", description="Solved 5 problems.", icon="Flame"),
            Achievement(type="PROBLEM_SOLVER_10", title="Problem Solver I", description="Solved 10 problems.", icon="Zap"),
            Achievement(type="PROBLEM_SOLVER_25", title="Problem Solver II", description="Solved 25 problems.", icon="Zap"),
            Achievement(type="PROBLEM_SOLVER_50", title="Problem Solver III", description="Solved 50 problems.", icon="Zap"),
            Achievement(type="DIFFICULTY_UP", title="Leveling Up", description="Graduated to a harder difficulty.", icon="TrendingUp"),
            Achievement(type="MEDIUM_UNLOCKED", title="Medium Unlocked", description="Reached Medium difficulty.", icon="Shield"),
            Achievement(type="HARD_UNLOCKED", title="Hard Unlocked", description="Reached Hard difficulty.", icon="Sword"),
            Achievement(type="ROADMAP_MILESTONE", title="Milestone Reached", description="Finished a core phase.", icon="Flag"),
            Achievement(type="ROADMAP_COMPLETED", title="DSA Master", description="Finished the entire roadmap.", icon="Crown")
        ]
        session.add_all(achievements)
        
        await session.commit()
        print(f"Successfully seeded database with {len(problems)} highly-curated DSA exercises and full curriculum!")

if __name__ == "__main__":
    asyncio.run(seed_data())

