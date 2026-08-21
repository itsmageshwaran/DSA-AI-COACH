"""Root router for API version 1."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.v1.agents import router as agents_router
from src.api.v1.ai import router as ai_router
from src.api.v1.auth import router as auth_router
from src.api.v1.courses import router as courses_router
from src.api.v1.execution import router as execution_router
from src.api.v1.exercises import router as exercises_router
from src.api.v1.health import router as health_router
from src.api.v1.knowledge import router as knowledge_router
from src.api.v1.learning_paths import router as learning_paths_router
from src.api.v1.lessons import router as lessons_router
from src.api.v1.modules import router as modules_router
from src.api.v1.progress import router as progress_router
from src.api.v1.submissions import router as submissions_router
from src.api.v1.tutor import router as tutor_router
from src.api.v1.learning_intelligence import router as learning_intelligence_router
from src.api.v1.users import router as users_router
from src.api.v1.billing import router as billing_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(billing_router, prefix="/billing", tags=["Billing & Enterprise"])

# Learning domain routers
api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])
api_router.include_router(modules_router, prefix="/modules", tags=["Modules"])
api_router.include_router(lessons_router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(learning_paths_router, prefix="/learning-paths", tags=["Learning Paths"])
api_router.include_router(exercises_router, prefix="/exercises", tags=["Exercises"])
api_router.include_router(progress_router, prefix="/progress", tags=["Progress"])
api_router.include_router(submissions_router, prefix="/submissions", tags=["Submissions"])
api_router.include_router(execution_router, prefix="/execution", tags=["Code Execution"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Gateway"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["Knowledge RAG"])
api_router.include_router(agents_router, prefix="/agents", tags=["Agent Framework"])
api_router.include_router(tutor_router, prefix="/ws/tutor", tags=["Tutor WebSockets"])
api_router.include_router(learning_intelligence_router)

from src.api.v1.recommendations import router as recommendations_router
api_router.include_router(recommendations_router)
