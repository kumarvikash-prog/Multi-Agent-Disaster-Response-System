"""Domain exceptions and FastAPI exception handlers.

Every module raises a typed AppError subclass. A single set of handlers
registered in main.py converts them into the standard error envelope.
Stack traces are never exposed to clients.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)

logger = logging.getLogger(__name__)


# ─── Standard error envelope ──────────────────────────────────────────────────


def _error_envelope(
    code: str,
    message: str,
    request_id: str,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build the standard JSON error envelope sent to all clients."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": request_id,
        }
    }


def _get_request_id(request: Request) -> str:
    """Extract the request-id injected by the middleware, or generate a fallback."""
    return str(getattr(request.state, "request_id", uuid.uuid4()))


# ─── Base application exception ───────────────────────────────────────────────


class AppError(Exception):
    """Base class for all domain / application exceptions.

    Raise domain-specific subclasses from services (e.g. ``IncidentNotFound``).
    The handler maps them to the error envelope automatically.
    """

    def __init__(
        self,
        code: str,
        http_status: int,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.message = message
        self.details = details or {}


# ─── Common reusable errors ───────────────────────────────────────────────────


class NotFoundError(AppError):
    """Resource does not exist or the caller is not authorised to see it."""

    def __init__(self, message: str = "Not found.") -> None:
        super().__init__(code="NOT_FOUND", http_status=404, message=message)


class ConflictError(AppError):
    """Operation conflicts with the current state (duplicate, stale version, etc.)."""

    def __init__(self, code: str = "CONFLICT", message: str = "Conflict.") -> None:
        super().__init__(code=code, http_status=409, message=message)


class ServiceUnavailableError(AppError):
    """A required dependency (database, LLM provider) is not reachable."""

    def __init__(self, message: str = "Service temporarily unavailable.") -> None:
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            http_status=HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
        )


# ─── Exception handlers ───────────────────────────────────────────────────────


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Convert any AppError (and subclass) into the standard error envelope."""
    request_id = _get_request_id(request)
    return JSONResponse(
        status_code=exc.http_status,
        content=_error_envelope(
            code=exc.code,
            message=exc.message,
            request_id=request_id,
            details=exc.details,
        ),
        headers={"X-Request-ID": request_id},
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Convert Pydantic validation errors into the standard 422 envelope."""
    request_id = _get_request_id(request)
    # Summarise which fields failed without leaking raw input values
    field_errors: dict[str, object] = {}
    for error in exc.errors():
        loc = " → ".join(str(p) for p in error["loc"])
        field_errors[loc] = error["msg"]

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_envelope(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            request_id=request_id,
            details={"fields": field_errors},
        ),
        headers={"X-Request-ID": request_id},
    )


async def csrf_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a 403 when the CSRF header check fails."""
    request_id = _get_request_id(request)
    return JSONResponse(
        status_code=HTTP_403_FORBIDDEN,
        content=_error_envelope(
            code="CSRF_HEADER_MISSING",
            message="Non-GET requests must include 'X-Requested-With: fetch'.",
            request_id=request_id,
        ),
        headers={"X-Request-ID": request_id},
    )


class CsrfHeaderMissingError(Exception):
    """Raised by middleware when the CSRF header is absent on a non-GET request."""


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected exceptions.

    Logs the full stack trace server-side but returns only a safe 500 to the client.
    """
    request_id = _get_request_id(request)
    logger.exception(
        "Unhandled exception",
        extra={"request_id": request_id, "path": request.url.path},
    )
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_envelope(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred. Please try again.",
            request_id=request_id,
        ),
        headers={"X-Request-ID": request_id},
    )
