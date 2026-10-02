# ADR-0002 — Cookie Auth via Render Rewrite Proxy

**Status:** Accepted (verify with Phase 0 spike)
**Date:** 2026-10-02

## Context

The frontend (React) and backend (FastAPI) are hosted as two separate Render services. We need HTTP-only cookies for JWT authentication. Cross-origin cookies are blocked or restricted by modern browsers (SameSite=Lax, Secure). We want both the browser and the backend to see the same origin.

## Decision

The Render **static site** has a rewrite rule: `/api/*` → `https://<backend>.onrender.com/api/*` (Rewrite, not Redirect). This makes all API calls appear to come from the same origin as the frontend, so `SameSite=Lax` cookies work correctly. The frontend uses relative `/api/v1/…` paths — identical in development (Vite proxy) and production (Render rewrite).

**Plan B:** If the cookie round-trip fails through the Render proxy, FastAPI will serve the built frontend via `StaticFiles` (single service, same origin). Record outcome as an update to this ADR.

## Consequences

**Good:** First-party cookies. No CORS configuration needed. Vite dev proxy mirrors production exactly.

**Bad:** Render rewrite rules must be configured correctly. The Phase 0 spike (§11.8, check 3) must verify cookie behaviour on Chrome, Firefox, and Safari/iOS before Phase 1 starts.

**Revisit when:** Render rewrite is confirmed unreliable → activate Plan B.
