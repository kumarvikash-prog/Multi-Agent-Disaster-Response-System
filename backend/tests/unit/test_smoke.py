"""Smoke tests for pure units (no I/O required).

Tests:
  - Configuration validation (JWT_SECRET length in production).
  - Priority scoring golden examples from §7.2.
  - Haversine distance sanity checks.
  - State machine legal and illegal transitions.
  - AI AnalysisOutput schema validation.
"""

from __future__ import annotations

import pytest

# ── Config ────────────────────────────────────────────────────────────────────


def test_config_development_does_not_require_long_jwt_secret() -> None:
    """In development mode a short JWT_SECRET must be accepted."""
    import os

    os.environ["ENV"] = "development"
    os.environ["DATABASE_URL"] = "postgresql+psycopg://localhost/disasterai_test"
    os.environ["JWT_SECRET"] = "short"

    from importlib import reload

    import app.core.config as cfg

    reload(cfg)
    settings = cfg.Settings()  # type: ignore[call-arg]
    assert settings.ENV == "development"


def test_config_production_rejects_short_jwt_secret() -> None:
    """In production a JWT_SECRET shorter than 32 chars must raise ValueError."""
    from pydantic import ValidationError

    import app.core.config as cfg

    with pytest.raises((ValueError, ValidationError)):
        cfg.Settings(
            ENV="production",
            DATABASE_URL="postgresql+psycopg://localhost/disasterai_test",
            JWT_SECRET="tooshort",
        )


# ── Priority scoring ──────────────────────────────────────────────────────────


def test_priority_score_collapse_critical() -> None:
    """Building collapse + 15 trapped + CRITICAL urgency ≈ 81 → CRITICAL (§7.2 golden example)."""
    from app.modules.triage.priority import compute_priority_score, score_to_level
    from app.shared.enums import HazardType, PriorityLevel, RiskFlag, Urgency

    score = compute_priority_score(
        hazard_types=[HazardType.BUILDING_COLLAPSE],
        people_count=15,
        urgency=Urgency.CRITICAL,
        risk_flags=[RiskFlag.TRAPPED_PEOPLE, RiskFlag.INJURIES],
    )
    assert score >= 75  # noqa: PLR2004
    assert score_to_level(score) == PriorityLevel.CRITICAL


def test_priority_score_small_fire_medium() -> None:
    """Small fire, no people, LOW urgency → MEDIUM (§7.2 golden example)."""
    from app.modules.triage.priority import compute_priority_score, score_to_level
    from app.shared.enums import HazardType, PriorityLevel, Urgency

    score = compute_priority_score(
        hazard_types=[HazardType.FIRE],
        people_count=0,
        urgency=Urgency.LOW,
        risk_flags=[],
    )
    assert 25 <= score < 50  # noqa: PLR2004
    assert score_to_level(score) == PriorityLevel.MEDIUM


def test_priority_score_no_hazards_returns_nonzero() -> None:
    """Even with no hazards the score must be non-negative."""
    from app.modules.triage.priority import compute_priority_score

    score = compute_priority_score(hazard_types=[], people_count=None, urgency=None, risk_flags=[])
    assert 0 <= score <= 100  # noqa: PLR2004


# ── Haversine ─────────────────────────────────────────────────────────────────


def test_haversine_same_point_is_zero() -> None:
    from app.modules.triage.geo import haversine_km

    assert haversine_km(28.0, 77.0, 28.0, 77.0) == 0.0


def test_haversine_is_symmetric() -> None:
    from app.modules.triage.geo import haversine_km

    d1 = haversine_km(28.6, 77.2, 19.1, 72.9)
    d2 = haversine_km(19.1, 72.9, 28.6, 77.2)
    assert abs(d1 - d2) < 0.001


def test_haversine_delhi_mumbai_approx() -> None:
    """Delhi → Mumbai is roughly 1150 km (known value)."""
    from app.modules.triage.geo import haversine_km

    dist = haversine_km(28.6139, 77.2090, 19.0760, 72.8777)
    assert 1100 < dist < 1200  # noqa: PLR2004


# ── State machine ─────────────────────────────────────────────────────────────


def test_state_machine_valid_transition() -> None:
    from app.modules.incidents.state_machine import assert_transition
    from app.shared.enums import IncidentStatus

    assert_transition(IncidentStatus.SUBMITTED, IncidentStatus.ANALYZING)  # must not raise


def test_state_machine_invalid_transition_raises() -> None:
    from app.core.errors import ConflictError
    from app.modules.incidents.state_machine import assert_transition
    from app.shared.enums import IncidentStatus

    with pytest.raises(ConflictError) as exc_info:
        assert_transition(IncidentStatus.SUBMITTED, IncidentStatus.RESOLVED)

    assert exc_info.value.code == "INVALID_STATE_TRANSITION"


def test_state_machine_terminal_state_raises() -> None:
    from app.core.errors import ConflictError
    from app.modules.incidents.state_machine import assert_transition
    from app.shared.enums import IncidentStatus

    with pytest.raises(ConflictError):
        assert_transition(IncidentStatus.RESOLVED, IncidentStatus.SUBMITTED)


# ── AI schemas ────────────────────────────────────────────────────────────────


def test_analysis_output_valid() -> None:
    from app.modules.ai.schemas import AnalysisOutput, ResourceCounts
    from app.shared.enums import HazardType, RiskFlag, Urgency

    output = AnalysisOutput(
        hazard_types=[HazardType.FIRE],
        urgency=Urgency.HIGH,
        risk_flags=[RiskFlag.INJURIES],
        required_resources=ResourceCounts(ambulance=2, fire_truck=1, rescue_team=0, medical_team=1),
        summary="Large fire reported at the market.",
    )
    assert output.urgency == Urgency.HIGH


def test_analysis_output_deduplicates_hazards() -> None:
    from app.modules.ai.schemas import AnalysisOutput, ResourceCounts
    from app.shared.enums import HazardType, Urgency

    output = AnalysisOutput(
        hazard_types=[HazardType.FIRE, HazardType.FIRE],
        urgency=Urgency.LOW,
        risk_flags=[],
        required_resources=ResourceCounts(ambulance=0, fire_truck=1, rescue_team=0, medical_team=0),
        summary="Duplicate hazard types should be deduplicated.",
    )
    assert len(output.hazard_types) == 1


def test_analysis_output_summary_too_long_fails() -> None:
    from pydantic import ValidationError

    from app.modules.ai.schemas import AnalysisOutput, ResourceCounts
    from app.shared.enums import HazardType, Urgency

    with pytest.raises(ValidationError):
        AnalysisOutput(
            hazard_types=[HazardType.OTHER],
            urgency=Urgency.LOW,
            risk_flags=[],
            required_resources=ResourceCounts(
                ambulance=0, fire_truck=0, rescue_team=0, medical_team=0
            ),
            summary="x" * 301,  # exceeds 300 char limit
        )
