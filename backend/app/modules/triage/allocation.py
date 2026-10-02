"""Allocation planning — pure function, no I/O.

Input: incident location, required unit counts, available units, available hospitals.
Output: a plan dict ready to be stored as ``recommendations.plan`` JSONB.

See §7.4 for the full spec. Key points:
  - Available units sorted by haversine distance; ties broken by call_sign ascending.
  - ETAs use DEFAULT_SPEED_KMH and are flagged estimate=true.
  - Hospital chosen only when ≥1 ambulance requested; nearest with available_beds ≥ 1.
  - Units are NOT reserved here; reservation happens atomically in workflow/approve.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.modules.triage.geo import haversine_km
from app.modules.triage.rules import DEFAULT_SPEED_KMH, MIN_ETA_MINUTES
from app.shared.enums import ResourceType


@dataclass
class AvailableUnit:
    """Snapshot of a single available response unit."""

    id: str
    type: ResourceType
    call_sign: str
    latitude: float
    longitude: float


@dataclass
class AvailableHospital:
    """Snapshot of a hospital with available capacity."""

    id: str
    name: str
    latitude: float
    longitude: float
    available_beds: int


@dataclass
class AllocationPlan:
    """Output of the allocation function."""

    units: list[dict[str, object]] = field(default_factory=list)
    hospital: dict[str, object] | None = None
    shortfall: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def _eta_minutes(distance_km: float) -> int:
    """Compute estimated travel time in whole minutes (minimum MIN_ETA_MINUTES)."""
    return max(MIN_ETA_MINUTES, math.ceil(distance_km / DEFAULT_SPEED_KMH * 60))


def compute_allocation(
    incident_lat: float,
    incident_lng: float,
    required: dict[ResourceType, int],
    available_units: list[AvailableUnit],
    available_hospitals: list[AvailableHospital],
) -> AllocationPlan:
    """Compute a dispatch recommendation.

    Args:
        incident_lat, incident_lng: Incident location.
        required: Desired unit counts per type (from LLM output after sanity clamping).
        available_units: All currently AVAILABLE units (caller loads from DB before calling).
        available_hospitals: All hospitals with available_beds ≥ 1.

    Returns:
        AllocationPlan with selected units, hospital, shortfall, and warnings.
    """
    plan = AllocationPlan()
    ambulance_assigned = 0

    for resource_type, count in required.items():
        if count <= 0:
            continue

        # Sort by distance (ascending), then call_sign (ascending) for determinism
        candidates = sorted(
            (u for u in available_units if u.type == resource_type),
            key=lambda u: (
                haversine_km(incident_lat, incident_lng, u.latitude, u.longitude),
                u.call_sign,
            ),
        )

        selected = candidates[:count]
        missing = count - len(selected)

        if missing > 0:
            plan.shortfall[resource_type.value] = missing
            plan.warnings.append(
                f"SHORTFALL: {missing} {resource_type.value}(s) requested but not available."
            )

        for unit in selected:
            distance_km = round(
                haversine_km(incident_lat, incident_lng, unit.latitude, unit.longitude), 2
            )
            plan.units.append(
                {
                    "id": unit.id,
                    "type": unit.type.value,
                    "call_sign": unit.call_sign,
                    "distance_km": distance_km,
                    "eta_minutes": _eta_minutes(distance_km),
                    "estimate": True,
                }
            )
            if resource_type == ResourceType.AMBULANCE:
                ambulance_assigned += 1

    # Hospital selection — only when ambulances are included
    if ambulance_assigned > 0 and available_hospitals:
        nearest = min(
            available_hospitals,
            key=lambda h: haversine_km(incident_lat, incident_lng, h.latitude, h.longitude),
        )
        distance_km = round(
            haversine_km(incident_lat, incident_lng, nearest.latitude, nearest.longitude), 2
        )
        plan.hospital = {
            "id": nearest.id,
            "name": nearest.name,
            "distance_km": distance_km,
            "available_beds": nearest.available_beds,
        }
    elif ambulance_assigned > 0:
        plan.warnings.append("NO_HOSPITAL_CAPACITY: No hospital with available beds found.")

    return plan
