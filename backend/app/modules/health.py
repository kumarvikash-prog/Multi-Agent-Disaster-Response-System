"""Health check endpoints.

GET /api/v1/health    — liveness probe; does NOT touch the database.
GET /api/v1/health/db — diagnostic; executes SELECT 1.

The liveness endpoint deliberately avoids any database call so that:
  - The Render keep-alive pinger does not wake Neon unnecessarily.
  - The endpoint always responds even when the database is down.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import check_database_reachable, get_session
from app.core.errors import ServiceUnavailableError
from app.shared.time import utcnow

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Liveness probe — returns immediately without opening a database session."""
    return {"status": "ok", "timestamp": utcnow().isoformat()}


@router.get("/health/db")
def health_db(db: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
    """Diagnostic probe — executes SELECT 1 to verify database connectivity.

    Returns 503 if the database is unreachable so monitoring can distinguish
    app-is-up from db-is-up.
    """
    if not check_database_reachable(db):
        raise ServiceUnavailableError("Database is not reachable.")
    return {"status": "ok", "db": "reachable", "timestamp": utcnow().isoformat()}
