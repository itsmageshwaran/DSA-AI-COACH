"""Users API endpoints (/api/v1/users)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.domain.auth.models import User
from src.modules.auth.dependencies import get_current_active_user
from src.modules.users.schemas import UserResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Retrieve profile details for currently authenticated user."""
    role_name = current_user.role.name if current_user.role else None
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        role=role_name,
        profile=current_user.profile,
        created_at=current_user.created_at,
    )


from src.modules.users.schemas import UserProfileUpdate, UserProfileResponse
from src.infrastructure.database.session import get_async_session
from src.infrastructure.database.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.auth.models import UserProfile

@router.post(
    "/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update or create user profile",
)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> UserProfileResponse:
    """Update user career goals and preferences."""
    async with UnitOfWork(session) as uow:
        profile = current_user.profile
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            uow.session.add(profile)
        
        if profile_data.career_goal is not None:
            profile.career_goal = profile_data.career_goal
        if profile_data.experience_level is not None:
            profile.experience_level = profile_data.experience_level
        if profile_data.preferred_language is not None:
            profile.preferred_language = profile_data.preferred_language
        
        profile.onboarding_completed = True
        
        await uow.commit()
        await uow.session.refresh(profile)
        
        return UserProfileResponse.model_validate(profile, from_attributes=True)
