"""Baseline HTTP hardening headers (a small, considered policy — not a penetration test).

TALIMGO's API returns JSON; the interface is a separate static app. That shapes the policy:

* ``X-Content-Type-Options: nosniff`` — stops a browser from re-interpreting a JSON body as HTML or
  script when a content type is missing or ambiguous.
* ``Referrer-Policy: no-referrer`` — TALIMGO URLs must not leak to third parties through referrers.
* ``X-Frame-Options: DENY`` plus ``frame-ancestors 'none'`` in the CSP — the API is never embeddable,
  so clickjacking of any future HTML the backend might serve is closed off.
* ``Permissions-Policy`` — every powerful browser feature the product does not use is switched off
  explicitly rather than left to the browser default.
* ``Content-Security-Policy`` — ``default-src 'none'`` for API responses. The interactive docs UI
  (development only) needs its own policy because Swagger UI loads its assets from a CDN; production
  serves no HTML at all from this service, so the strict policy always applies there.
* ``Strict-Transport-Security`` — only ever sent on a request that arrived over HTTPS. Sending HSTS
  over plain HTTP is meaningless (browsers ignore it) and would break local development, so it is
  derived from the request, never from a static flag.

Deliberately not set, with reasons: ``Cross-Origin-Opener-Policy``/``Cross-Origin-Embedder-Policy``
(they govern *documents*; this service serves JSON) and ``Cross-Origin-Resource-Policy`` (it restricts
no-CORS embedding, which the browser's CORS check already covers for this API, and it would risk
breaking the legitimate cross-origin dev frontend). ``Server`` header removal is a reverse-proxy
concern and is documented in the deployment guide instead.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import Response

# Feature list: everything a learner-facing learning API/interface does not need. Additions must be
# justified by an actual feature (e.g. enabling `microphone` would require a product decision).
PERMISSIONS_POLICY = ", ".join(
    f"{feature}=()"
    for feature in (
        "accelerometer",
        "ambient-light-sensor",
        "autoplay",
        "battery",
        "camera",
        "display-capture",
        "document-domain",
        "encrypted-media",
        "fullscreen",
        "geolocation",
        "gyroscope",
        "hid",
        "idle-detection",
        "magnetometer",
        "microphone",
        "midi",
        "payment",
        "picture-in-picture",
        "publickey-credentials-get",
        "screen-wake-lock",
        "serial",
        "usb",
        "xr-spatial-tracking",
    )
)

API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; sandbox"

# Swagger UI (development only) loads its own bundle and style from a CDN, and the OpenAPI JSON
# from this origin. Everything else stays blocked, including framing.
DOCS_CSP = (
    "default-src 'none'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "font-src 'self' https://cdn.jsdelivr.net; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
)

DOCS_PREFIXES = ("/api/docs", "/api/openapi.json")

HSTS_VALUE = "max-age=31536000"


def _is_https(request: Request) -> bool:
    """True when the request reached us over TLS (directly or through a reverse proxy).

    ``X-Forwarded-Proto`` is only trustworthy behind a proxy that overwrites it, which the
    deployment guide requires; a forged header can only *add* HSTS to a response, never weaken it.
    """
    forwarded = request.headers.get("x-forwarded-proto", "")
    scheme = (forwarded.split(",")[0].strip() or request.url.scheme).lower()
    return scheme == "https"


def hardening_headers(request: Request) -> dict[str, str]:
    """The header set for one response. Pure, so it can be unit-tested without a server."""
    path = request.url.path
    headers = {
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "X-Frame-Options": "DENY",
        "Permissions-Policy": PERMISSIONS_POLICY,
        "Content-Security-Policy": DOCS_CSP if path.startswith(DOCS_PREFIXES) else API_CSP,
    }
    if _is_https(request):
        headers["Strict-Transport-Security"] = HSTS_VALUE
    return headers


async def apply_hardening_headers(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware: attach the policy to every response, including errors and preflights."""
    response = await call_next(request)
    for name, value in hardening_headers(request).items():
        response.headers.setdefault(name, value)
    return response
