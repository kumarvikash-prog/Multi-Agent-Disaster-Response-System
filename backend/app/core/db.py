"""Database engine and session factory.

Uses synchronous SQLAlchemy 2.x with psycopg 3 (synchronous driver).
Connection pool is tuned for Neon's pooler compatibility.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _build_connect_args() -> dict[str, object]:
    """psycopg 3 connect_args tuned for Neon's pgBouncer pooler.

    prepare_threshold=None disables prepared statements, which pgBouncer
    (transaction-mode pooler) does not support.
    connect_timeout prevents hanging on a cold Neon database wake-up.
    """
    return {
        "connect_timeout": 10,
        "prepare_threshold": None,
    }


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # detect stale connections before handing them to the app
    pool_recycle=300,  # recycle connections every 5 min (avoids idle-timeout drops)
    pool_size=5,
    max_overflow=5,
    connect_args=_build_connect_args(),
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # avoid lazy-load after commit in the same request
)


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base.

    All ORM models inherit from this class.
    """


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session.

    The session is closed (and the connection returned to the pool) after
    the request finishes, even if an exception is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_reachable(db: Session) -> bool:
    """Execute a lightweight query to verify database connectivity.

    Returns True if the database responds; False if an error occurs.
    Used by GET /api/v1/health/db.
    """
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
