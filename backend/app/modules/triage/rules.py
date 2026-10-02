"""Triage rules — weights, thresholds, and sanity floors.

All magic numbers live here. Changing a number → re-run the golden-example tests.
This module is imported by priority.py, allocation.py, and the test suite.
"""

from __future__ import annotations

from app.shared.enums import HazardType, PriorityLevel, ResourceType, RiskFlag, Urgency

# ── Priority score weights (must sum to 1.0) ──────────────────────────────────
WEIGHT_HAZARD: float = 0.35
WEIGHT_PEOPLE: float = 0.30
WEIGHT_URGENCY: float = 0.25
WEIGHT_RISK: float = 0.10

# ── Hazard weights ────────────────────────────────────────────────────────────
HAZARD_WEIGHTS: dict[HazardType, float] = {
    HazardType.BUILDING_COLLAPSE: 0.90,
    HazardType.EARTHQUAKE: 0.90,
    HazardType.FIRE: 0.85,
    HazardType.FLOOD: 0.75,
    HazardType.LANDSLIDE: 0.70,
    HazardType.ROAD_ACCIDENT: 0.60,
    HazardType.OTHER: 0.40,
}

# Bonus per additional hazard type (added to the max single-hazard weight)
HAZARD_MULTI_BONUS: float = 0.05  # identical to RISK_FLAG_STEP for simplicity

# ── Urgency weights ───────────────────────────────────────────────────────────
URGENCY_WEIGHTS: dict[Urgency, float] = {
    Urgency.LOW: 0.25,
    Urgency.MEDIUM: 0.50,
    Urgency.HIGH: 0.75,
    Urgency.CRITICAL: 1.00,
}

# ── People factor ─────────────────────────────────────────────────────────────
# log10(1 + 100) ≈ 2.004 → people_factor reaches 1.0 at 100 people
PEOPLE_LOG_DENOMINATOR: int = 101

# ── Risk factor ───────────────────────────────────────────────────────────────
RISK_FLAG_STEP: float = 0.34  # per flag; three flags → capped at 1.0

# ── Priority level thresholds ─────────────────────────────────────────────────
LEVEL_THRESHOLDS: dict[PriorityLevel, int] = {
    PriorityLevel.CRITICAL: 75,
    PriorityLevel.HIGH: 50,
    PriorityLevel.MEDIUM: 25,
    PriorityLevel.LOW: 0,
}

# ── Allocation ────────────────────────────────────────────────────────────────
MAX_UNITS_PER_TYPE: int = 10  # clamp LLM-suggested counts
DEFAULT_SPEED_KMH: float = 60.0  # assumed average speed for ETA calculation
MIN_ETA_MINUTES: int = 1  # minimum ETA even for on-site resources

# ── Sanity floors — applied after LLM output is clamped ─────────────────────
# Format: {HazardType | RiskFlag: {ResourceType: min_count}}
# These are checked in order; a hazard type overrides a risk flag if both apply.
SANITY_FLOORS: list[tuple[HazardType | RiskFlag, dict[ResourceType, int]]] = [
    (HazardType.FIRE, {ResourceType.FIRE_TRUCK: 1}),
    (HazardType.BUILDING_COLLAPSE, {ResourceType.RESCUE_TEAM: 1, ResourceType.AMBULANCE: 1}),
    (
        HazardType.EARTHQUAKE,
        {
            ResourceType.RESCUE_TEAM: 1,
            ResourceType.AMBULANCE: 1,
            ResourceType.MEDICAL_TEAM: 1,
        },
    ),
    (RiskFlag.TRAPPED_PEOPLE, {ResourceType.RESCUE_TEAM: 1}),
    (RiskFlag.INJURIES, {ResourceType.AMBULANCE: 1}),
]

# ── Fallback resource table — used when AI analysis failed ────────────────────
FALLBACK_RESOURCES: dict[HazardType, dict[ResourceType, int]] = {
    HazardType.FIRE: {ResourceType.FIRE_TRUCK: 1},
    HazardType.BUILDING_COLLAPSE: {ResourceType.RESCUE_TEAM: 1, ResourceType.AMBULANCE: 1},
    HazardType.EARTHQUAKE: {
        ResourceType.RESCUE_TEAM: 1,
        ResourceType.AMBULANCE: 1,
        ResourceType.MEDICAL_TEAM: 1,
    },
    HazardType.FLOOD: {ResourceType.RESCUE_TEAM: 1},
    HazardType.LANDSLIDE: {ResourceType.RESCUE_TEAM: 1},
    HazardType.ROAD_ACCIDENT: {ResourceType.AMBULANCE: 1},
    HazardType.OTHER: {},
}
