"""Password security, hashing, and verification using bcrypt."""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against stored bcrypt hash."""
    pw_bytes = plain_password.encode("utf-8")[:72]
    hash_bytes = hashed_password.encode("utf-8")
    return bool(bcrypt.checkpw(pw_bytes, hash_bytes))


def validate_password_policy(password: str) -> None:
    """Validate password against security policy requirements.

    Policy: Minimum 8 characters, contains uppercase, lowercase, and a digit.
    """
    if len(password) < 8:
        msg = "Password must be at least 8 characters long"
        raise ValueError(msg)
    if not any(c.isupper() for c in password):
        msg = "Password must contain at least one uppercase letter"
        raise ValueError(msg)
    if not any(c.islower() for c in password):
        msg = "Password must contain at least one lowercase letter"
        raise ValueError(msg)
    if not any(c.isdigit() for c in password):
        msg = "Password must contain at least one digit"
        raise ValueError(msg)
