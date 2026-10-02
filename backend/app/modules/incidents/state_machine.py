"""Incident state machine.

Enforces the valid transition table from §7.1.
Raise ``InvalidStateTransition`` (→ HTTP 409) for any illegal transition.
"""

from __future__ import annotations

from app.core.errors import ConflictError
from app.shared.enums import IncidentStatus

# (from_status, to_status) → who can trigger it
_VALID_TRANSITIONS: set[tuple[IncidentStatus, IncidentStatus]] = {
    (IncidentStatus.SUBMITTED, IncidentStatus.ANALYZING),  # system (claim)
    (IncidentStatus.ANALYZING, IncidentStatus.PENDING_REVIEW),  # system (analysis done)
    (IncidentStatus.ANALYZING, IncidentStatus.SUBMITTED),  # system (sweep re-queue)
    (IncidentStatus.SUBMITTED, IncidentStatus.SUBMITTED),  # system (sweep, idempotent)
    (IncidentStatus.PENDING_REVIEW, IncidentStatus.DISPATCHED),  # authority (approve)
    (IncidentStatus.PENDING_REVIEW, IncidentStatus.REJECTED),  # authority (reject)
    (IncidentStatus.DISPATCHED, IncidentStatus.RESOLVED),  # authority (resolve)
}

# Terminal states — no transition out is ever legal
_TERMINAL_STATES: frozenset[IncidentStatus] = frozenset(
    {
        IncidentStatus.RESOLVED,
        IncidentStatus.REJECTED,
    }
)


def assert_transition(current: IncidentStatus, target: IncidentStatus) -> None:
    """Raise ``InvalidStateTransition`` if the transition is not in the allowed table.

    Args:
        current: The incident's current status.
        target:  The desired next status.

    Raises:
        ConflictError: With code ``INVALID_STATE_TRANSITION`` if not permitted.
    """
    if current in _TERMINAL_STATES:
        raise ConflictError(
            code="INVALID_STATE_TRANSITION",
            message=f"Incident is in terminal state {current!r} and cannot be transitioned.",
        )
    if (current, target) not in _VALID_TRANSITIONS:
        raise ConflictError(
            code="INVALID_STATE_TRANSITION",
            message=(
                f"Cannot transition from {current!r} to {target!r}. "
                f"Allowed: {sorted(str(t) for _, t in _VALID_TRANSITIONS if _ == current)}"
            ),
        )
