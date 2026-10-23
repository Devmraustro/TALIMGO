"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.config import get_settings
from app.deps import SESSION_COOKIE_NAME, CurrentUser, Db, client_ip
from app.schemas import LoginRequest, MeOut, ProfileOut, RegisterRequest, UserOut
from app.services import accounts
from app.utils import utcnow

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str, max_age_seconds: int, *, secure: bool) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=max_age_seconds,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )


@router.post("/register", response_model=MeOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Db) -> MeOut:
    settings = get_settings()
    try:
        user = accounts.register_user(
            db,
            settings,
            email=str(payload.email),
            password=payload.password,
            display_name=payload.display_name,
            accept_terms=payload.accept_terms,
            accept_ai_processing=payload.accept_ai_processing,
        )
    except accounts.EmailAlreadyRegistered as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except accounts.WeakPasswordError as exc:
        raise HTTPException(status_code=422, detail={"problems": exc.problems}) from exc
    except accounts.AccountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    token = accounts.create_session(db, settings, user)
    _set_session_cookie(
        response, token, settings.session_ttl_hours * 3600, secure=settings.env == "production"
    )
    profile = accounts.get_profile(db, user)
    return MeOut(
        user=UserOut.model_validate(user),
        profile=ProfileOut.model_validate(profile),
        consents=[
            {"kind": row.kind, "granted": row.granted, "recorded_at": row.recorded_at}
            for row in accounts.list_consents(db, user)
        ],
    )


@router.post("/login", response_model=MeOut)
def login(payload: LoginRequest, request: Request, response: Response, db: Db) -> MeOut:
    settings = get_settings()
    try:
        user = accounts.authenticate(
            db,
            settings,
            email=str(payload.email),
            password=payload.password,
            ip=client_ip(request),
            now=utcnow(),
        )
    except accounts.AccountLocked as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except accounts.InvalidCredentials as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    token = accounts.create_session(db, settings, user)
    _set_session_cookie(
        response, token, settings.session_ttl_hours * 3600, secure=settings.env == "production"
    )
    profile = accounts.get_profile(db, user)
    return MeOut(
        user=UserOut.model_validate(user),
        profile=ProfileOut.model_validate(profile),
        consents=[
            {"kind": row.kind, "granted": row.granted, "recorded_at": row.recorded_at}
            for row in accounts.list_consents(db, user)
        ],
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Db) -> Response:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        accounts.revoke_session(db, token)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=MeOut)
def me(user: CurrentUser, db: Db) -> MeOut:
    profile = accounts.get_profile(db, user)
    return MeOut(
        user=UserOut.model_validate(user),
        profile=ProfileOut.model_validate(profile),
        consents=[
            {"kind": row.kind, "granted": row.granted, "recorded_at": row.recorded_at}
            for row in accounts.list_consents(db, user)
        ],
    )
