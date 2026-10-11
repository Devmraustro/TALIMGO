"""Application entry point.

Composition only: configuration validation, middleware, routers, and startup that prepares the
database. Business logic lives in ``app/services`` and the deterministic engine in ``app/learning``.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.db import Base, get_engine, session_scope
from app.http_hardening import apply_hardening_headers
from app.request_guards import apply_request_guards
from app.routers import (
    admin,
    auth,
    curriculum,
    dashboard,
    diagnostic,
    goals,
    health,
    me,
    plans,
    practice,
    tutor,
)

logger = logging.getLogger("talimgo")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def _prepare_database() -> None:
    """Development/test convenience: create tables and load authored curriculum.

    Production expects Alembic migrations to have been applied (see the README) and does not create
    schema implicitly.
    """
    settings = get_settings()
    engine = get_engine()
    existing = set(inspect(engine).get_table_names())

    if settings.env == "production":
        if "objectives" not in existing:
            raise RuntimeError(
                "Database schema is missing. Run `alembic upgrade head` before starting in production."
            )
        return

    if not existing:
        Base.metadata.create_all(engine)

    from app.curriculum.loader import load_all

    with session_scope() as db:
        counts = load_all(db)
    logger.info("Curriculum loaded: %s", counts)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(
        "TALIMGO starting env=%s ai_enabled=%s ai_dialect=%s local_only=yes",
        settings.env,
        settings.ai_enabled,
        settings.ai_dialect,
    )
    _prepare_database()
    yield
    logger.info("TALIMGO shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="TALIMGO API",
        version="0.1.0",
        description=(
            "TALIMGO backend. Generative AI runs only on locally hosted, self-hosted models; "
            "there is no hosted provider integration."
        ),
        lifespan=lifespan,
        docs_url="/api/docs" if settings.env != "production" else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if settings.env != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["content-type", "authorization"],
    )

    # Guards run inside CORS (so preflights are answered) and before routing (so a rejected request
    # never reaches a handler): JSON-only bodies and a declared size limit (app/request_guards.py).
    app.middleware("http")(apply_request_guards)

    # Registered last, so it is the outermost layer: successful responses, guard rejections, error
    # responses and CORS preflight replies all carry the same policy (app/http_hardening.py).
    app.middleware("http")(apply_hardening_headers)

    for router in (
        health.router,
        auth.router,
        me.router,
        curriculum.router,
        goals.router,
        diagnostic.router,
        plans.router,
        dashboard.router,
        practice.router,
        tutor.router,
        admin.router,
    ):
        app.include_router(router)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        # Field names only; never echo submitted values back (they may contain content or secrets).
        fields = [".".join(str(part) for part in error.get("loc", ())) for error in exc.errors()]
        return JSONResponse(
            status_code=422,
            content={"detail": "Request validation failed.", "fields": sorted(set(fields))},
        )

    @app.exception_handler(Exception)
    async def unhandled_error(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", exc.__class__.__name__)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. The incident was logged."},
        )

    return app


app = create_app()
