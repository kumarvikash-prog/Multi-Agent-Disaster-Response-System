# ADR-0003 — Straight-Line Distance in Phase 1

**Status:** Accepted
**Date:** 2026-10-02

## Context

The resource allocation plan needs to rank available units by distance from the incident to determine which units are dispatched and compute estimated ETAs. Using a real routing engine (OSRM, Google Maps API) requires external network calls during the AI analysis pipeline, adds latency, and introduces a dependency on external rate limits.

## Decision

Phase 1 uses **haversine (great-circle) straight-line distance** implemented as a pure Python function in `triage/geo.py`. ETAs are computed as `ceil(distance_km / DEFAULT_SPEED_KMH × 60)` with a minimum of 1 minute, and are always flagged `estimate: true` in the response.

Plain `latitude` / `longitude` columns (double precision) are used instead of PostGIS geography types, because 50 units and 20 hospitals need no spatial index.

## Consequences

**Good:** Zero external dependencies in the allocation pipeline. Fully testable with known city-pair distances. No PostGIS extension needed in Phase 1.

**Bad:** Distances ignore road topology, traffic, and terrain. ETAs are approximations. The frontend must always display them as estimates.

**Revisit when:** Phase 2 — integrate OSRM (open-source, self-hosted) for road-based routing. At that point migrate to PostGIS `GEOGRAPHY(Point, 4326)` columns and add spatial indexes.
