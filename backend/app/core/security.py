"""Security helpers: password hashing, JWT encode/decode, token generation.

These are pure utilities with no database access.
Business endpoints (register, login, refresh) live in the auth module.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import bcrypt
import jwt
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError

from app.core.config import settings

# JWT claims we set
_ACCESS_TOKEN_TYPE = "access"  # noqa: S105
_REFRESH_TOKEN_TYPE = "refresh"  # noqa: S105
_ALGORITHM = "HS256"
_CLOCK_SKEW_SECONDS = 10  # tolerate minor clock drift between services


# ─── Password ─────────────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt cost 12.

    Raises ValueError if the password is empty, < 8 bytes, or > 72 bytes.
    bcrypt silently truncates beyond 72 bytes, which would allow bypass.
    We reject it explicitly.
    """
    encoded = plain.encode("utf-8")
    if len(encoded) < 8:  # noqa: PLR2004
        raise ValueError("Password must be at least 8 bytes.")
    if len(encoded) > 72:  # noqa: PLR2004
        raise ValueError(
            "Password must not exceed 72 bytes. "
            "bcrypt would silently truncate it, which is a security risk."
        )
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Compare a plain-text password against a bcrypt hash.

    Always runs bcrypt.checkpw regardless of whether the hash looks valid,
    to maintain a constant-time response and avoid timing attacks.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ─── JWT ──────────────────────────────────────────────────────────────────────


def encode_access_token(user_id: str, role: str) -> str:
    """Create a signed JWT access token (15-minute lifetime by default)."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": user_id,
        "role": role,
        "type": _ACCESS_TOKEN_TYPE,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Raises jwt.InvalidTokenError (or subclass) on any failure.
    The caller should map these to 401 AppErrors.
    """
    return cast(
        dict[str, Any],
        jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[_ALGORITHM],
            leeway=timedelta(seconds=_CLOCK_SKEW_SECONDS),
            options={"require": ["sub", "role", "type", "exp"]},
        ),
    )


# ─── Refresh token ────────────────────────────────────────────────────────────


def generate_opaque_token() -> str:
    """Generate a cryptographically secure 256-bit opaque refresh token.

    The raw token is sent to the client; only the SHA-256 hash is stored.
    """
    return secrets.token_urlsafe(32)


def hash_token(raw: str) -> str:
    """Return the SHA-256 hex digest of a refresh token for storage."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# Re-export jwt exception types so callers don't import jwt directly
__all__ = [
    "hash_password",
    "verify_password",
    "encode_access_token",
    "decode_access_token",
    "generate_opaque_token",
    "hash_token",
    "DecodeError",
    "ExpiredSignatureError",
    "InvalidTokenError",
]
