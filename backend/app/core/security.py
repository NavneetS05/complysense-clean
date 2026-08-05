# Use: Utility functions for password hashing (bcrypt), verification, and JWT encoding/decoding.
# Note: bcrypt has a hard 72-byte limit. Passwords are explicitly truncated before hashing/verifying.

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# PASSWORD
# ---------------------------------------------------------------------------


def _truncate_password(plain_password: str) -> bytes:
    """bcrypt enforces a hard 72-byte limit. Pre-truncate so behaviour is explicit."""
    return plain_password.encode("utf-8")[:72]


def hash_password(plain_password: str) -> str:
    return password_context.hash(_truncate_password(plain_password))


def verify_password(plain_password: str, password_hash: str) -> bool:
    return password_context.verify(_truncate_password(plain_password), password_hash)


# ---------------------------------------------------------------------------
# ACCESS TOKEN
# ---------------------------------------------------------------------------


def create_access_token(subject: str, claims: dict[str, Any]) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at, "type": "access", **claims}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


# ---------------------------------------------------------------------------
# REFRESH TOKEN
# ---------------------------------------------------------------------------


def create_refresh_token(subject: str, session_id: str) -> str:
    """Refresh tokens are longer-lived JWTs tied to a specific session_id.

    On rotation the old session is deleted and a new one is created —
    the new refresh token encodes the new session_id.
    """
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expires_at,
        "type": "refresh",
        "session_id": session_id,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


# ---------------------------------------------------------------------------
# DECODE / VALIDATE
# ---------------------------------------------------------------------------


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT. Raises jose.JWTError on any failure."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


# ---------------------------------------------------------------------------
# RESET TOKEN
# ---------------------------------------------------------------------------


def generate_reset_token() -> str:
    """Generate a cryptographically secure URL-safe reset token."""
    return secrets.token_urlsafe(32)
