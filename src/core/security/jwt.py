"""JWT Token generation, verification, and decoding utilities."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt

from src.core.config.settings import settings


class InvalidTokenError(Exception):
    """Raised when token verification fails."""


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    claims: dict[str, Any] | None = None,
) -> str:
    """Generate a JWT access token for a subject (user ID)."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "type": "access",
        "jti": str(uuid.uuid4()),
    }
    if claims:
        to_encode.update(claims)

    return str(jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm))


def create_refresh_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a JWT refresh token for a subject (user ID)."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.refresh_token_expire_days)

    to_encode: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return str(jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm))


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token signature and expiration."""
    try:
        decoded: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return decoded
    except JWTError as err:
        msg = "Could not validate credentials"
        raise InvalidTokenError(msg) from err
