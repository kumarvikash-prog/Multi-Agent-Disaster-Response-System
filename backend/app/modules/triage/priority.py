"""Priority scoring — pure function, no I/O.

Formula (§7.2):
  score = round(100 × (0.35·hazard + 0.30·people + 0.25·urgency + 0.10·risk))

Levels:  ≥75 CRITICAL · ≥50 HIGH · ≥25 MEDIUM · else LOW

All weights and thresholds live in triage/rules.py and are tested with golden examples.
"""

from __future__ import annotations

import math

from app.modules.triage.rules import (
    HAZARD_WEIGHTS,
    LEVEL_THRESHOLDS,
    PEOPLE_LOG_DENOMINATOR,
    RISK_FLAG_STEP,
    URGENCY_WEIGHTS,
    WEIGHT_HAZARD,
    WEIGHT_PEOPLE,
    WEIGHT_RISK,
    WEIGHT_URGENCY,
)
from app.shared.enums import HazardType, PriorityLevel, RiskFlag, Urgency


def _hazard_factor(hazard_types: list[HazardType]) -> float:
    """Compute the hazard factor: highest single weight + 0.05 per extra hazard (max 1.0)."""
    if not hazard_types:
        return HAZARD_WEIGHTS.get(HazardType.OTHER, 0.40)

    max_weight = max(HAZARD_WEIGHTS.get(h, 0.40) for h in hazard_types)
    extra_bonus = RISK_FLAG_STEP * (len(hazard_types) - 1)
    return min(1.0, max_weight + extra_bonus)


def _people_factor(people_count: int | None) -> float:
    """Compute the people factor using a log10 scale.

    null / 0 → 0.0
    15 people → ~0.60
    100 people → 1.0 (capped)
    """
    if not people_count:  # None or 0
        return 0.0
    return min(1.0, math.log10(1 + people_count) / math.log10(PEOPLE_LOG_DENOMINATOR))


def _urgency_factor(urgency: Urgency | None) -> float:
    """Compute the urgency factor; defaults to MEDIUM weight if not set."""
    return URGENCY_WEIGHTS.get(urgency or Urgency.MEDIUM, 0.50)


def _risk_factor(risk_flags: list[RiskFlag]) -> float:
    """Compute the risk factor: 0.34 per flag, capped at 1.0."""
    return min(1.0, RISK_FLAG_STEP * len(risk_flags))


def compute_priority_score(
    hazard_types: list[HazardType],
    people_count: int | None,
    urgency: Urgency | None,
    risk_flags: list[RiskFlag],
) -> int:
    """Compute the 0–100 priority score from the four weighted factors."""
    score = (
        WEIGHT_HAZARD * _hazard_factor(hazard_types)
        + WEIGHT_PEOPLE * _people_factor(people_count)
        + WEIGHT_URGENCY * _urgency_factor(urgency)
        + WEIGHT_RISK * _risk_factor(risk_flags)
    )
    return round(100 * score)


def score_to_level(score: int) -> PriorityLevel:
    """Map a numeric score to the corresponding priority level."""
    if score >= LEVEL_THRESHOLDS[PriorityLevel.CRITICAL]:
        return PriorityLevel.CRITICAL
    if score >= LEVEL_THRESHOLDS[PriorityLevel.HIGH]:
        return PriorityLevel.HIGH
    if score >= LEVEL_THRESHOLDS[PriorityLevel.MEDIUM]:
        return PriorityLevel.MEDIUM
    return PriorityLevel.LOW
