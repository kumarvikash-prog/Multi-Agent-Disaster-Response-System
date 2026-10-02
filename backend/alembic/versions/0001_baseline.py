"""Baseline migration — Phase 0 foundation.

This migration is intentionally minimal: it only creates the incident_code
sequence used to generate human-readable INC-XXXXXX codes.
All business tables (users, incidents, resources, etc.) are added in Phase 1
milestones (M1.1–M1.3) as the schema stabilises.

Downgrade: drops the sequence.
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create the incident code sequence."""
    op.execute(
        sa.text(
            "CREATE SEQUENCE IF NOT EXISTS incident_code_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE"
        )
    )


def downgrade() -> None:
    """Drop the incident code sequence."""
    op.execute(sa.text("DROP SEQUENCE IF EXISTS incident_code_seq"))
