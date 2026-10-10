"""Learner account controls: profile, preferences, consents, export and deletion."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from app.deps import SESSION_COOKIE_NAME, CurrentUser, Db
from app.schemas import ConsentIn, ConsentOut, DataExportOut, DeleteAccountIn, ProfileOut, ProfileUpdate
from app.services import accounts
from app.utils import utcnow

router = APIRouter(prefix="/api/me", tags=["account"])


@router.get("/profile", response_model=ProfileOut)
def get_profile(user: CurrentUser, db: Db) -> ProfileOut:
    return ProfileOut.model_validate(accounts.get_profile(db, user))


@router.patch("/profile", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, user: CurrentUser, db: Db) -> ProfileOut:
    profile = accounts.get_profile(db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    from app.utils import utcnow as _now

    profile.updated_at = _now()
    db.commit()
    return ProfileOut.model_validate(profile)


@router.get("/consents", response_model=list[ConsentOut])
def list_consents(user: CurrentUser, db: Db) -> list[ConsentOut]:
    return [ConsentOut.model_validate(row) for row in accounts.list_consents(db, user)]


@router.post("/consents", response_model=ConsentOut)
def set_consent(payload: ConsentIn, user: CurrentUser, db: Db) -> ConsentOut:
    row = accounts.set_consent(db, user, payload.kind, payload.granted)
    return ConsentOut.model_validate(row)


@router.get("/export", response_model=DataExportOut)
def export_data(user: CurrentUser, db: Db) -> DataExportOut:
    data = accounts.export_account(db, user)
    return DataExportOut(
        exported_at=utcnow(),
        account=data,
        notice=(
            "This file contains everything TALIMGO stores about your account, including your "
            "evidence records and mastery estimates. Model conversation text is included; lesson "
            "content and other learners' data are not."
        ),
    )


@router.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(payload: DeleteAccountIn, user: CurrentUser, db: Db, response: Response) -> Response:
    try:
        accounts.delete_account(db, user, password=payload.password)
    except accounts.InvalidCredentials as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
