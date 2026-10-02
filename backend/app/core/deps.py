"""FastAPI dependency functions.

These are the building blocks for route-level auth and role enforcement.
Implementation is deferred to M1.1 (auth module); placeholders raise
501 to make any premature usage visible immediately.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# TODO(M1.1): implement current_user and require_role after the auth module exists.

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    _credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> None:
    """Placeholder for the authenticated user dependency.

    Will be replaced in M1.1 to decode the JWT from the HttpOnly cookie
    and return the user object.
    """
    # Not yet implemented — auth endpoints are wired in M1.1
    return None


async def require_authority() -> None:
    """Placeholder for AUTHORITY role guard.

    Will be replaced in M1.1 to raise 403 when the caller is not an authority.
    """
    return None
