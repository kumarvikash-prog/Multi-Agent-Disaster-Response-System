"""Modules package: assembles all module routers into a single API router."""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.health import router as health_router

api_router = APIRouter()

# ── Health (always first — no auth, no DB for /health) ───────────────────────
api_router.include_router(health_router, tags=["health"])

# ── Phase 1 module routers (wired in their respective milestones) ─────────────
# TODO(M1.1): api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
# TODO(M1.2): api_router.include_router(resources_router, prefix="/resources", tags=["resources"])
# TODO(M1.2): api_router.include_router(hospitals_router, prefix="/hospitals", tags=["hospitals"])
# TODO(M1.3): api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
# TODO(M1.3): api_router.include_router(incidents_router, prefix="/incidents", tags=["incidents"])
