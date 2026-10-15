"""Tutor endpoint — the only route that reaches the local model.

Every failure mode is explicit: AI disabled, no local runtime, invalid model output, or the daily
allowance exhausted. There is no fallback provider.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.ai.adapter import LocalModelResponseError, LocalModelUnavailable
from app.ai.grounding import GroundingMismatchError
from app.ai.schemas import TutorOutputRejected
from app.ai.tutor import AiBudgetExceededError, AiBusyError, AiDisabledError, answer, usage_today
from app.config import get_settings
from app.deps import CurrentUser, Db
from app.models import ConsentRecord, Objective, TutorMessage, TutorThread
from app.schemas import TutorAskIn, TutorReplyOut

logger = logging.getLogger("talimgo.tutor")

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


def _ai_consent_granted(db: Db, user_id: str) -> bool:
    row = db.scalar(
        select(ConsentRecord).where(ConsentRecord.user_id == user_id, ConsentRecord.kind == "ai_processing")
    )
    return bool(row and row.granted)


@router.post("/ask", response_model=TutorReplyOut)
def ask(payload: TutorAskIn, user: CurrentUser, db: Db) -> TutorReplyOut:
    settings = get_settings()
    objective = db.get(Objective, payload.objective_id)
    if objective is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown objective.")

    if not _ai_consent_granted(db, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Tutoring needs your consent for AI processing. It runs on TALIMGO's own servers and "
                "your content is never sent to an external AI provider."
            ),
        )

    profile_locale = "en"
    from app.models import Profile

    profile = db.get(Profile, user.id)
    if profile is not None:
        profile_locale = profile.locale

    try:
        result = answer(
            db,
            settings,
            user=user,
            objective_id=payload.objective_id,
            lesson_id=payload.lesson_id,
            question=payload.question,
            locale=profile_locale,
        )
    except GroundingMismatchError as exc:
        # The lesson named does not belong to the objective: refuse before any prompt is built, so
        # the model is never called with mismatched material.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That lesson does not belong to that objective.",
        ) from exc
    except AiDisabledError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AiBudgetExceededError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except AiBusyError as exc:
        logger.warning("local model concurrency cap reached")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Tutoring is at capacity right now. Try again shortly; this request did not consume "
                "today's tutoring allowance."
            ),
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc
    except LocalModelUnavailable as exc:
        # Explicit failure: the learner is told tutoring is offline; nothing else is contacted. The
        # endpoint address and the transport error class go to the log, not to the learner (the same
        # rule as the response-error branch below).
        logger.warning("local model unavailable: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Tutoring is unavailable right now: the local model did not answer. Your message "
                "was not sent anywhere else. The request still counts against today's tutoring limit."
            ),
        ) from exc
    except LocalModelResponseError as exc:
        # The runtime answered but TALIMGO cannot use the answer: HTTP error status, non-JSON body or
        # an empty completion. The learner gets a fixed, safe sentence — never the upstream status
        # line, body, model output or a traceback. Operators get the detail in the server log, which
        # is where diagnostics belong (the reserved quota slot is intentionally not refunded).
        logger.warning("local model returned an unusable response: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The local model returned a response TALIMGO could not use, so nothing was shown "
                "or stored. The request still counts against today's tutoring limit."
            ),
        ) from exc
    except TutorOutputRejected as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The local model produced an answer that failed TALIMGO's validation, so it was not "
                "shown. Nothing was stored. Try rephrasing your question."
            ),
        ) from exc

    db.commit()
    return TutorReplyOut(**result)


@router.get("/usage")
def usage(user: CurrentUser, db: Db) -> dict:
    settings = get_settings()
    return {
        "ai_enabled": settings.ai_enabled,
        "endpoint_is_local": True,  # enforced by configuration validation, verified by tests
        "model_configured": bool(settings.ai_model),
        "used_today": usage_today(db, user.id),
        "daily_limit": settings.ai_daily_requests_per_learner,
        "policy": "local-only inference; no hosted AI provider is used at any point",
    }


@router.get("/threads")
def threads(user: CurrentUser, db: Db) -> list[dict]:
    rows = db.scalars(
        select(TutorThread)
        .where(TutorThread.user_id == user.id)
        .order_by(TutorThread.created_at.desc())
        .limit(20)
    ).all()
    output = []
    for thread in rows:
        messages = db.scalars(
            select(TutorMessage).where(TutorMessage.thread_id == thread.id).order_by(TutorMessage.created_at)
        ).all()
        output.append(
            {
                "id": thread.id,
                "objective_id": thread.objective_id,
                "lesson_id": thread.lesson_id,
                "created_at": thread.created_at,
                "messages": [
                    {
                        "role": message.role,
                        "content": message.content,
                        "created_at": message.created_at,
                        "validation": message.validation,
                    }
                    for message in messages
                ],
            }
        )
    return output
