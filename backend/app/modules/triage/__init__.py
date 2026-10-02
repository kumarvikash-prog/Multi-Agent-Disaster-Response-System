"""Triage module public API.

Only these symbols are visible to other modules.
"""

from app.modules.triage.allocation import (
    AllocationPlan,
    AvailableHospital,
    AvailableUnit,
    compute_allocation,
)
from app.modules.triage.geo import haversine_km
from app.modules.triage.priority import compute_priority_score, score_to_level

__all__ = [
    "compute_priority_score",
    "score_to_level",
    "haversine_km",
    "compute_allocation",
    "AllocationPlan",
    "AvailableUnit",
    "AvailableHospital",
]
