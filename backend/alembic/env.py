"""Alembic environment configuration.

Reads DATABASE_URL_DIRECT (for migrations) or falls back to DATABASE_URL.
Uses the SQLAlchemy metadata from all modules (auto-generates migrations).
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Alembic config ────────────────────────────────────────────────────────────
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Use DATABASE_URL_DIRECT for migrations (bypasses the pgBouncer pooler) ───
db_url = os.environ.get("DATABASE_URL_DIRECT") or os.environ.get("DATABASE_URL", "")
if not db_url:
    raise RuntimeError("DATABASE_URL or DATABASE_URL_DIRECT must be set before running Alembic.")

config.set_main_option("sqlalchemy.url", db_url)

# ── Import the shared Base and all model modules so autogenerate sees them ────
from app.core.db import Base  # noqa: E402

# TODO: import models as they are created:
# from app.modules.users.models import *       # noqa: F401, F403
# from app.modules.incidents.models import *   # noqa: F401, F403
# from app.modules.resources.models import *   # noqa: F401, F403
# from app.modules.hospitals.models import *   # noqa: F401, F403
# from app.modules.audit.models import *       # noqa: F401, F403

target_metadata = Base.metadata

# ── Naming convention for constraints (reproducible migration names) ──────────

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
target_metadata.naming_convention = naming_convention


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection, generates SQL)."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (requires a live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Alembic should not pool connections
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
