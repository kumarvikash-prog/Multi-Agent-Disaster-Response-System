"""Shared enumerations used across the entire backend.

Values are stored in the database as VARCHAR strings (not Postgres native enums)
so they can be evolved without a migration that rewrites the type.
"""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    """User roles enforced by RBAC middleware."""

    CITIZEN = "CITIZEN"
    AUTHORITY = "AUTHORITY"


class IncidentStatus(StrEnum):
    """Lifecycle states of an incident (§7.1 state machine)."""

    SUBMITTED = "SUBMITTED"
    ANALYZING = "ANALYZING"
    PENDING_REVIEW = "PENDING_REVIEW"
    DISPATCHED = "DISPATCHED"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class HazardType(StrEnum):
    """Disaster / hazard categories understood by the system."""

    BUILDING_COLLAPSE = "BUILDING_COLLAPSE"
    EARTHQUAKE = "EARTHQUAKE"
    FIRE = "FIRE"
    FLOOD = "FLOOD"
    LANDSLIDE = "LANDSLIDE"
    ROAD_ACCIDENT = "ROAD_ACCIDENT"
    OTHER = "OTHER"


class ResourceType(StrEnum):
    """Types of response units that can be dispatched."""

    AMBULANCE = "AMBULANCE"
    FIRE_TRUCK = "FIRE_TRUCK"
    RESCUE_TEAM = "RESCUE_TEAM"
    MEDICAL_TEAM = "MEDICAL_TEAM"


class ResourceStatus(StrEnum):
    """Availability state of a response unit."""

    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"


class Urgency(StrEnum):
    """AI-assessed urgency level (also used for overrides)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PriorityLevel(StrEnum):
    """Computed priority level derived from the priority score."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskFlag(StrEnum):
    """Known risk flags that the AI can identify in a report."""

    TRAPPED_PEOPLE = "TRAPPED_PEOPLE"
    INJURIES = "INJURIES"
    FIRE_SPREADING = "FIRE_SPREADING"
    HAZMAT = "HAZMAT"
    STRUCTURAL_DAMAGE = "STRUCTURAL_DAMAGE"
    CHILDREN_OR_ELDERLY = "CHILDREN_OR_ELDERLY"
    ROAD_BLOCKED = "ROAD_BLOCKED"


class AuditAction(StrEnum):
    """Actions recorded in the append-only audit_logs table."""

    USER_REGISTERED = "USER_REGISTERED"
    REPORT_SUBMITTED = "REPORT_SUBMITTED"
    ANALYSIS_STARTED = "ANALYSIS_STARTED"
    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    PRIORITY_COMPUTED = "PRIORITY_COMPUTED"
    RECOMMENDATION_CREATED = "RECOMMENDATION_CREATED"
    INCIDENT_EDITED = "INCIDENT_EDITED"
    PRIORITY_OVERRIDDEN = "PRIORITY_OVERRIDDEN"
    INCIDENT_APPROVED = "INCIDENT_APPROVED"
    UNITS_ASSIGNED = "UNITS_ASSIGNED"
    INCIDENT_REJECTED = "INCIDENT_REJECTED"
    INCIDENT_RESOLVED = "INCIDENT_RESOLVED"
    UNITS_RELEASED = "UNITS_RELEASED"
    HOSPITAL_UPDATED = "HOSPITAL_UPDATED"
    SWEEP_REQUEUED = "SWEEP_REQUEUED"


class ActorType(StrEnum):
    """Who caused an audit log entry."""

    USER = "USER"
    AI = "AI"
    SYSTEM = "SYSTEM"


class AssignmentStatus(StrEnum):
    """Lifecycle of a resource assignment."""

    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


class RecommendationStatus(StrEnum):
    """Lifecycle of a dispatch recommendation."""

    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    APPROVED = "APPROVED"


class AnalysisStatus(StrEnum):
    """Outcome of an AI analysis attempt."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
