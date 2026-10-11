"""Request guards: cheap, explicit bounds applied before any handler runs.

Two controls, both deliberately narrow:

* **JSON-only bodies on state-changing methods.** Every mutating endpoint in TALIMGO takes JSON.
  Rejecting other content types with 415 removes the classic cross-site form POST from the attack
  surface (a browser can send a cross-site form with `text/plain`, `application/x-www-form-urlencoded`
  or `multipart/form-data`, but never with `application/json`, which needs a preflight), so CSRF
  depends on the cookie's `SameSite=Lax` *and* on a request shape a cross-site form cannot produce.
  Requests with no body at all (e.g. logout) stay allowed.
* **Declared body size.** A request that announces more than ``settings.max_request_bytes`` is refused
  with 413 before it is read. A chunked body with no declared length on a mutating method is refused
  with 411 rather than read without bound.

Both are defence in depth: a reverse proxy must still cap body size and rate (docs/DEPLOYMENT.md),
because these checks trust the declared `Content-Length`.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings

MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
JSON_CONTENT_TYPE = "application/json"


def _content_type(request: Request) -> str:
    return request.headers.get("content-type", "").split(";")[0].strip().lower()


def guard_rejection(request: Request) -> JSONResponse | None:
    """The refusal response for this request, or None when it may proceed. Pure and testable."""
    if request.method not in MUTATING_METHODS:
        return None

    settings = get_settings()
    declared = request.headers.get("content-length")
    chunked = "chunked" in request.headers.get("transfer-encoding", "").lower()

    if declared is None and chunked:
        return JSONResponse(
            status_code=411,
            content={
                "detail": "A body must declare its length; chunked requests are not accepted.",
            },
        )

    if declared is not None:
        try:
            length = int(declared)
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Malformed Content-Length."})
        if length > settings.max_request_bytes:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": "Request body too large.",
                    "limit_bytes": settings.max_request_bytes,
                },
            )
        if length > 0 and _content_type(request) != JSON_CONTENT_TYPE:
            return JSONResponse(
                status_code=415,
                content={"detail": "Send this request as JSON (content-type: application/json)."},
            )

    return None


async def apply_request_guards(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    rejection = guard_rejection(request)
    if rejection is not None:
        return rejection
    return await call_next(request)
