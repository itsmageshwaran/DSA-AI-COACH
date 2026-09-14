"""Deterministic & Idempotent Presentation Demo Account Seeder."""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.security.password import hash_password
from src.domain.auth.models import User, UserProfile
from src.domain.learning.models import Achievement, Enrollment, Exercise, LearningPath, Progress, Submission, UserAchievement
from src.infrastructure.database.session import AsyncSessionFactory


async def seed_demo_account() -> None:
    """Seed or update presentation demo account idempotently."""
    email = "demo@kalvium.com"
    raw_password = "DemoPassword123!"

    async with AsyncSessionFactory() as session:
        # 1. Check if user exists
        stmt = select(User).where(User.email == email)
        user = (await session.execute(stmt)).scalars().first()

        hashed_pw = hash_password(raw_password)

        if not user:
            user = User(
                email=email,
                hashed_password=hashed_pw,
                full_name="Kalvium Demo Candidate",
                is_active=True,
                is_superuser=False,
            )
            session.add(user)
            await session.flush()
            print(f"Created demo user: {email}")
        else:
            user.hashed_password = hashed_pw
            user.is_active = True
            user.full_name = "Kalvium Demo Candidate"
            await session.flush()
            print(f"Updated credentials for demo user: {email}")

        # 2. Configure Profile
        prof_stmt = select(UserProfile).where(UserProfile.user_id == user.id)
        profile = (await session.execute(prof_stmt)).scalars().first()

        if not profile:
            profile = UserProfile(
                user_id=user.id,
                career_goal="Backend Engineering",
                experience_level="Intermediate",
                preferred_language="python",
                onboarding_completed=True,
            )
            session.add(profile)
        else:
            profile.career_goal = "Backend Engineering"
            profile.experience_level = "Intermediate"
            profile.preferred_language = "python"
            profile.onboarding_completed = True

        await session.flush()

        # 3. Ensure Enrollment in DSA Mastery
        path_stmt = select(LearningPath).where(LearningPath.title == "DSA Mastery")
        path = (await session.execute(path_stmt)).scalars().first()
        if path:
            enr_stmt = select(Enrollment).where(
                Enrollment.user_id == user.id,
                Enrollment.learning_path_id == path.id
            )
            enrollment = (await session.execute(enr_stmt)).scalars().first()
            if not enrollment:
                enrollment = Enrollment(user_id=user.id, learning_path_id=path.id)
                session.add(enrollment)
                await session.flush()

        # 4. Seed initial achievements
        achieve_stmt = select(Achievement).limit(3)
        initial_achievements = (await session.execute(achieve_stmt)).scalars().all()
        for ach in initial_achievements:
            ua_stmt = select(UserAchievement).where(
                UserAchievement.user_id == user.id,
                UserAchievement.achievement_id == ach.id
            )
            if not (await session.execute(ua_stmt)).scalars().first():
                session.add(UserAchievement(user_id=user.id, achievement_id=ach.id))

        await session.commit()
        print("Presentation demo account setup complete and verified!")


if __name__ == "__main__":
    asyncio.run(seed_demo_account())
