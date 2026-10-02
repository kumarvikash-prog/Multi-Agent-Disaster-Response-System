"""FastAPI application factory.

Creates and configures the FastAPI app instance:
  - JSON structured logging
  - Middleware (request-id, CSRF, body-size, security headers)
  - Exception handlers (AppError, validation, CSRF, 500 catch-all)
  - API router mounted at /api/v1
  - Health endpoints
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.errors import (
    AppError,
    CsrfHeaderMissingError,
    app_error_handler,
    csrf_error_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.modules import api_router


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan hook.

    Startup: configure logging, run startup sweep (added in M1.4).
    Shutdown: nothing to clean up for a sync app.
    """
    configure_logging(level="DEBUG" if settings.ENV == "development" else "INFO")
    # TODO(M1.4): run workflow.sweep.sweep_stuck_incidents() here
    yield


def create_app() -> FastAPI:
    """Construct and return the FastAPI application.

    Separating creation from the module-level scope allows importing the factory
    in tests without side effects.
    """
    app = FastAPI(
        title="DisasterAI",
        description=(
            "Multi-Agent Disaster Response System API. "
            "Citizens report emergencies; AI analyses and prioritises; "
            "authority reviews and dispatches."
        ),
        version="0.0.1",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/openapi.json",
        lifespan=_lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(RequestContextMiddleware)

    # ── Exception handlers ────────────────────────────────────────────────────
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(CsrfHeaderMissingError, csrf_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── API router ────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    return app


# Module-level app instance used by uvicorn: ``uvicorn app.main:app``
app = create_app()
