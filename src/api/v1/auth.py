"""Auth API endpoints (/api/v1/auth)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from src.infrastructure.database.dependencies import get_unit_of_work
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.modules.auth.schemas import (
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from src.modules.auth.service import (
    authenticate_user,
    create_tokens_for_user,
    logout_user,
    refresh_tokens,
    register_user,
)
from src.modules.users.schemas import UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: RegisterRequest,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> UserResponse:
    """Register a new user account."""
    user = await register_user(uow, payload)
    role_name = user.role.name if user.role else None
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        role=role_name,
        created_at=user.created_at,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue tokens",
)
async def login(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> TokenResponse:
    """Authenticate user credentials using JSON body or form data."""
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = str(form.get("username") or form.get("email") or "")
        password = str(form.get("password") or "")
    else:
        body = await request.json()
        email = str(body.get("email") or body.get("username") or "")
        password = str(body.get("password") or "")

    user = await authenticate_user(uow, email=email, password=password)
    return await create_tokens_for_user(uow, user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh(
    payload: RefreshRequest,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> TokenResponse:
    """Issue a new access and refresh token pair using a valid refresh token."""
    return await refresh_tokens(uow, payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke refresh token",
)
async def logout(
    payload: LogoutRequest,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> dict[str, str]:
    """Revoke active refresh token on logout."""
    await logout_user(uow, payload.refresh_token)
    return {"message": "Successfully logged out"}
