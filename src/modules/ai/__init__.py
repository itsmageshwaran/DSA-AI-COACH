"""AI module package."""

from src.modules.ai.schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    SocraticHintRequest,
    SocraticHintResponse,
)
from src.modules.ai.service import AIService, ai_service

__all__ = [
    "AIGenerateRequest",
    "AIGenerateResponse",
    "AIService",
    "SocraticHintRequest",
    "SocraticHintResponse",
    "ai_service",
]
