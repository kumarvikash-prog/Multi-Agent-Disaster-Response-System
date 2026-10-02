"""AI pipeline smoke tests — uses a fake/stub LLM, never calls real Gemini.

These tests verify:
  - AnalysisOutput schema rejects invalid enum values.
  - AnalysisOutput schema rejects resource counts outside 0–10.
"""

from __future__ import annotations

import pytest


def test_analysis_output_rejects_unknown_hazard() -> None:
    from pydantic import ValidationError

    from app.modules.ai.schemas import AnalysisOutput, ResourceCounts
    from app.shared.enums import Urgency

    with pytest.raises(ValidationError):
        AnalysisOutput(
            hazard_types=["VOLCANO"],  # type: ignore[list-item]  # not a valid HazardType
            urgency=Urgency.HIGH,
            risk_flags=[],
            required_resources=ResourceCounts(
                ambulance=1, fire_truck=0, rescue_team=0, medical_team=0
            ),
            summary="Unknown hazard type should be rejected.",
        )


def test_analysis_output_rejects_count_above_max() -> None:
    from pydantic import ValidationError

    from app.modules.ai.schemas import AnalysisOutput, ResourceCounts
    from app.shared.enums import HazardType, Urgency

    with pytest.raises(ValidationError):
        AnalysisOutput(
            hazard_types=[HazardType.FLOOD],
            urgency=Urgency.MEDIUM,
            risk_flags=[],
            required_resources=ResourceCounts(
                ambulance=11,  # exceeds max of 10
                fire_truck=0,
                rescue_team=0,
                medical_team=0,
            ),
            summary="Count above max should be rejected.",
        )
