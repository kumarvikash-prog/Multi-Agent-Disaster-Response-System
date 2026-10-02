"""Haversine distance calculation — pure function, no I/O.

Uses the haversine formula to compute the great-circle distance between two
(lat, lng) coordinate pairs in kilometres. Results are deterministic and
accurate enough for the distances involved in Phase 1 (city-scale).

PostGIS spatial queries will replace this in Phase 2 (ADR-0003).
"""

from __future__ import annotations

import math

_EARTH_RADIUS_KM: float = 6371.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return the great-circle distance between two WGS-84 coordinates, in km.

    Args:
        lat1, lng1: First point (decimal degrees).
        lat2, lng2: Second point (decimal degrees).

    Returns:
        Distance in kilometres (≥ 0).

    Examples:
        >>> round(haversine_km(28.6139, 77.2090, 19.0760, 72.8777), 1)
        1149.9  # Delhi → Mumbai ≈ 1150 km
        >>> haversine_km(0, 0, 0, 0)
        0.0
    """
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2
    return _EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
