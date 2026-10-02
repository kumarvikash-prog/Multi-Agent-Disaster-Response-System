"""Request middleware: request-id, CSRF header check, body-size limit, security headers.

All error responses are returned directly from the middleware dispatch method.
Do NOT raise exceptions from BaseHTTPMiddleware — Starlette wraps them in an
ExceptionGroup which prevents app-level handlers from catching them."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

logger = logging.getLogger(__name__)

# HTTP methods that must carry the CSRF header
_CSRF_ENFORCED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Security headers added to every response
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request-id to every request and log the completed request.

    Request lifecycle:
      1. Generate / accept ``X-Request-ID``.
      2. Store it on ``request.state.request_id``.
      3. Check body size (reject > ``MAX_BODY_SIZE_BYTES`` immediately).
      4. Check CSRF header on non-GET requests.
      5. Process the request.
      6. Attach security headers and ``X-Request-ID`` to the response.
      7. Emit a structured access log.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Body size guard — reject before reading the body
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.MAX_BODY_SIZE_BYTES:
            err_response = JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": "BODY_TOO_LARGE",
                        "message": (
                            f"Request body must not exceed {settings.MAX_BODY_SIZE_BYTES} bytes."
                        ),
                        "details": {},
                        "request_id": request_id,
                    }
                },
            )
            self._add_headers(err_response, request_id)
            return err_response

        # CSRF header check on non-GET requests — return 403 directly
        if request.method in _CSRF_ENFORCED_METHODS:
            if request.headers.get("X-Requested-With") != "fetch":
                resp = JSONResponse(
                    status_code=403,
                    content={
                        "error": {
                            "code": "CSRF_HEADER_MISSING",
                            "message": "Non-GET requests must include 'X-Requested-With: fetch'.",
                            "details": {},
                            "request_id": request_id,
                        }
                    },
                )
                self._add_headers(resp, request_id)
                return resp

        start = time.monotonic()
        response = await call_next(request)
        duration_ms = round((time.monotonic() - start) * 1000)

        self._add_headers(response, request_id)

        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                # user_id will be added here after auth is implemented (M1.1)
                "user_id": None,
            },
        )

        return response

    @staticmethod
    def _add_headers(response: Response, request_id: str) -> None:
        """Attach security headers and the request-id to the outgoing response."""
        response.headers["X-Request-ID"] = request_id
        for header, value in _SECURITY_HEADERS.items():
            response.headers[header] = value
