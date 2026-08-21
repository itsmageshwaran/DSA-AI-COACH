"""Auth module Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Registration request payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User plaintext password")
    full_name: str | None = Field(None, description="Optional full name")


class LoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User plaintext password")


class TokenResponse(BaseModel):
    """JWT Token response payload."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Refresh token request payload."""

    refresh_token: str = Field(..., description="Valid refresh token string")


class LogoutRequest(BaseModel):
    """Logout request payload."""

    refresh_token: str = Field(..., description="Refresh token to revoke")
