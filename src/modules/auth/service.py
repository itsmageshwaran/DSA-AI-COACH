"""Authentication business services."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from src.core.config.settings import settings
from src.core.security.jwt import create_access_token, create_refresh_token, decode_token
from src.core.security.password import hash_password, validate_password_policy, verify_password
from src.domain.auth.models import RefreshToken, User
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from src.infrastructure.repositories.user_repository import UserRepository
from src.modules.auth.schemas import RegisterRequest, TokenResponse


async def register_user(uow: UnitOfWork, payload: RegisterRequest) -> User:
    """Validate payload, hash password, and create new User."""
    try:
        validate_password_policy(payload.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    user_repo = UserRepository(uow.session)
    existing_user = await user_repo.get_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered",
        )

    hashed_pw = hash_password(payload.password)
    user = User(
        email=payload.email,
        hashed_password=hashed_pw,
        full_name=payload.full_name,
        is_active=True,
        is_superuser=False,
    )
    created_user = await user_repo.create(user)
    await uow.commit()
    return created_user


async def authenticate_user(uow: UnitOfWork, email: str, password: str) -> User:
    """Verify user credentials and return user if valid."""
    user_repo = UserRepository(uow.session)
    user = await user_repo.get_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    return user


async def create_tokens_for_user(uow: UnitOfWork, user: User) -> TokenResponse:
    """Create access token and refresh token for user, persisting refresh token."""
    role_name = user.role.name if user.role else "user"
    claims = {"role": role_name}
    access_token = create_access_token(subject=user.id, claims=claims)
    refresh_token_str = create_refresh_token(subject=user.id)

    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    token_record = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=expires_at,
        is_revoked=False,
    )
    token_repo = RefreshTokenRepository(uow.session)
    await token_repo.create(token_record)
    await uow.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)


async def refresh_tokens(uow: UnitOfWork, refresh_token_str: str) -> TokenResponse:
    """Validate refresh token and issue new token pair."""
    payload = decode_token(refresh_token_str)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    token_repo = RefreshTokenRepository(uow.session)
    token_record = await token_repo.get_by_token(refresh_token_str)
    if not token_record or token_record.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or invalid",
        )

    user_repo = UserRepository(uow.session)
    user = await user_repo.get_by_id_with_role(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer active",
        )

    # Revoke old refresh token
    token_record.is_revoked = True

    # Generate new token pair
    return await create_tokens_for_user(uow, user)


async def logout_user(uow: UnitOfWork, refresh_token_str: str) -> None:
    """Revoke provided refresh token."""
    token_repo = RefreshTokenRepository(uow.session)
    revoked = await token_repo.revoke_token(refresh_token_str)
    if revoked:
        await uow.commit()
