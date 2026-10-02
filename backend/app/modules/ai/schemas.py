"""AI module — Pydantic schemas for LLM input/output.

``AnalysisOutput`` is the ONLY thing the LLM produces.
It is validated against this model before being stored.
People count is NOT produced by the model — it comes from the citizen form.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.shared.enums import HazardType, RiskFlag, Urgency


class ResourceCounts(BaseModel):
    """Required response unit counts suggested by the LLM (0–10 each)."""

    ambulance: int = Field(ge=0, le=10)
    fire_truck: int = Field(ge=0, le=10)
    rescue_team: int = Field(ge=0, le=10)
    medical_team: int = Field(ge=0, le=10)


class AnalysisOutput(BaseModel):
    """Validated output of the AI analysis agent.

    Every field is constrained; the LLM cannot produce values outside these bounds.
    Unknown enum values are rejected (strict parsing).
    """

    model_config = {"extra": "forbid", "str_strip_whitespace": True}

    hazard_types: list[HazardType] = Field(
        min_length=1,
        max_length=4,
        description="Detected hazard types; deduplicated; unknown values are rejected.",
    )
    urgency: Urgency
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    required_resources: ResourceCounts
    summary: str = Field(
        max_length=300,
        description="Short English summary of the incident. No URLs, no instructions.",
    )

    @field_validator("hazard_types")
    @classmethod
    def deduplicate_hazard_types(cls, v: list[HazardType]) -> list[HazardType]:
        """Remove duplicates while preserving order."""
        seen: set[HazardType] = set()
        return [h for h in v if not (h in seen or seen.add(h))]  # type: ignore[func-returns-value]

    @field_validator("summary")
    @classmethod
    def strip_control_characters(cls, v: str) -> str:
        """Strip ASCII control characters (< 0x20 except tab/newline) from the summary."""
        return "".join(c for c in v if c >= " " or c in "\t\n")
