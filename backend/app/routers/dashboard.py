"""Dashboard: one primary next action, explained by the evidence behind it."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from app.deps import CurrentLocale, CurrentUser, Db
from app.schemas import DashboardOut, GoalOut, NextActionOut
from app.services.progress import build_dashboard

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def dashboard(user: CurrentUser, db: Db, locale: CurrentLocale) -> DashboardOut:
    data = build_dashboard(db, user, locale=locale)
    payload = dict(data)
    if payload.get("goal") is not None:
        payload["goal"] = GoalOut.model_validate(payload["goal"])
    # The selection engine returns a frozen dataclass; the API exposes a schema.
    payload["next_action"] = NextActionOut(**asdict(payload["next_action"]))
    return DashboardOut(**payload)
