"""Seed script — inserts default resources and hospitals idempotently.

Run after migrations:
    python scripts/seed.py

Uses call_sign / hospital name as the upsert key.
Does NOT overwrite hospital bed counts edited by the authority (unless --force).

TODO(M1.2): implement the actual upserts when models and migrations exist.
"""

from __future__ import annotations

# TODO(M1.2): implement
if __name__ == "__main__":
    print("Seed script not yet implemented (M1.2).")  # noqa: T201
