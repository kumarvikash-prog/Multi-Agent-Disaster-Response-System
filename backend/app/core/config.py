"""Application settings loaded from environment variables via pydantic-settings.

The app refuses to start with an invalid configuration. All settings are
validated at import time when the module-level ``settings`` singleton is created.
"""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration object.

    Values are read from environment variables (case-insensitive) and,
    in development, from a ``.env`` file in the ``backend/`` directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # tolerate unrecognised env vars gracefully
    )

    # ── Environment ──────────────────────────────────────────────────────────
    ENV: str = Field(default="development", description="development | production | test")

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        ...,
        description=(
            "Pooled connection string used by the app (psycopg 3 dialect). "
            "Example: postgresql+psycopg://user:pass@host/dbname"
        ),
    )
    DATABASE_URL_DIRECT: str | None = Field(
        default=None,
        description=(
            "Direct (non-pooled) connection string used by Alembic for migrations. "
            "Falls back to DATABASE_URL if not set."
        ),
    )

    # ── Auth / Security ───────────────────────────────────────────────────────
    JWT_SECRET: str = Field(
        default="dev-secret-change-me-in-production-must-be-32-chars",
        description="HS256 signing secret. Must be ≥ 32 chars in production.",
    )
    JWT_ACCESS_EXPIRE_MINUTES: int = Field(default=15)
    JWT_REFRESH_EXPIRE_DAYS: int = Field(default=7)
    COOKIE_SECURE: bool = Field(
        default=False,
        description="Set to true in production (HTTPS only). False for local HTTP.",
    )

    # ── Google / LLM ─────────────────────────────────────────────────────────
    GOOGLE_API_KEY: str | None = Field(default=None)
    LLM_PROVIDER: str = Field(default="google_genai")
    LLM_MODEL: str | None = Field(default=None)
    LLM_RPM: int = Field(default=8, description="Max LLM requests per minute.")
    LLM_MAX_CONCURRENCY: int = Field(default=2)

    # ── Request / Body limits ─────────────────────────────────────────────────
    MAX_BODY_SIZE_BYTES: int = Field(default=100_000, description="100 KB max request body.")

    # ── Rate limits (in-memory, single-process) ───────────────────────────────
    LOGIN_RATE_PER_MINUTE: int = Field(default=5)
    REGISTER_RATE_PER_HOUR: int = Field(default=10)
    REPORT_RATE_LIMIT_PER_HOUR: int = Field(default=5)

    # ── Service area (optional, used in M1.3+) ────────────────────────────────
    SERVICE_AREA_BBOX: str | None = Field(
        default=None,
        description="Optional bounding box: 'min_lat,min_lng,max_lat,max_lng'",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def database_url_must_use_psycopg_dialect(cls, v: str) -> str:
        """Enforce the psycopg 3 dialect prefix."""
        if not v.startswith("postgresql+psycopg://"):
            raise ValueError(
                "DATABASE_URL must use the 'postgresql+psycopg://' dialect prefix. "
                f"Received: {v!r}"
            )
        return v

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Settings:
        """In production, require a strong JWT_SECRET and no missing critical values."""
        if self.ENV == "production":
            if len(self.JWT_SECRET) < 32:  # noqa: PLR2004
                raise ValueError(
                    "JWT_SECRET must be at least 32 characters in production. "
                    "Set it via the environment variable."
                )
        return self

    def __repr__(self) -> str:
        """Never expose secrets in repr/logs."""
        return (
            f"Settings(ENV={self.ENV!r}, LLM_PROVIDER={self.LLM_PROVIDER!r}, "
            f"JWT_SECRET=<redacted>, DATABASE_URL=<redacted>)"
        )


# Module-level singleton — imported everywhere as ``from app.core.config import settings``
settings = Settings()  # type: ignore[call-arg]
