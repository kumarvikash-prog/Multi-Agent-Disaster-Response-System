"""Timezone-aware UTC datetime helpers.

All timestamps in DisasterAI are UTC. Never use naive datetimes.
"""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware).

    Use this everywhere instead of ``datetime.utcnow()`` (which returns naive).
    """
    return datetime.now(UTC)
