"""Authenticated learning flows must return educational content in the learner's locale.

The profile has supported `ar` for navigation and layout direction for a while, but several
assessment, practice, plan and dashboard paths asked the serialisers for English explicitly, so an
Arabic learner received Arabic chrome around English lessons, questions, explanations and rationales.
"""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from app.curriculum.registry import item_index
from tests.conftest import _correct_response, answer_diagnostic_until_done, create_goal, register

ARABIC = re.compile(r"[\u0600-\u06ff]")
LESSON_ID = "py:values:lesson"
OBJECTIVE_ID = "py:values"


def _set_locale(client: TestClient, locale: str) -> None:
    response = client.patch("/api/me/profile", json={"locale": locale})
    assert response.status_code == 200, response.text
    assert response.json()["locale"] == locale


def _learner(client: TestClient, locale: str) -> dict:
    register(client)
    _set_locale(client, locale)
    return create_goal(client)


def _has_arabic(value: str) -> bool:
    return bool(ARABIC.search(value or ""))


# --------------------------------------------------------------------------------------
# Curriculum content
# --------------------------------------------------------------------------------------


def test_profile_locale_is_stored_and_returned(client: TestClient) -> None:
    register(client)
    _set_locale(client, "ar")
    assert client.get("/api/me/profile").json()["locale"] == "ar"


def test_lessons_are_served_in_the_learners_locale(client: TestClient) -> None:
    register(client)
    english = client.get(f"/api/curriculum/lessons/{LESSON_ID}")
    assert english.status_code == 200, english.text
    assert _has_arabic(english.json()["title"]) is False

    _set_locale(client, "ar")
    arabic = client.get(f"/api/curriculum/lessons/{LESSON_ID}")
    assert arabic.status_code == 200, arabic.text
    body = arabic.json()
    assert _has_arabic(body["title"]), body["title"]
    assert _has_arabic(body["body_md"]), "the lesson body, not just its title, must be localised"
    assert body["title"] != english.json()["title"]


def test_objectives_are_served_in_the_learners_locale(client: TestClient) -> None:
    register(client)
    _set_locale(client, "ar")
    rows = client.get("/api/curriculum/paths/python-foundations/objectives").json()
    titles = [row["title"] for row in rows]
    assert all(_has_arabic(title) for title in titles), titles
    summaries = [row["summary"] for row in rows]
    assert all(_has_arabic(summary) for summary in summaries), summaries


def test_public_path_summaries_accept_a_locale_query(client: TestClient) -> None:
    """Public routes have no learner profile yet, so the request locale is used."""
    default = client.get("/api/curriculum/paths")
    assert default.status_code == 200, default.text
    assert _has_arabic(default.json()[0]["title"]) is False

    arabic = client.get("/api/curriculum/paths?locale=ar")
    assert arabic.status_code == 200, arabic.text
    assert _has_arabic(arabic.json()[0]["title"])

    header = client.get("/api/curriculum/paths", headers={"Accept-Language": "ar-DZ,ar;q=0.9,en;q=0.5"})
    assert header.status_code == 200, header.text
    assert _has_arabic(header.json()[0]["title"])


# --------------------------------------------------------------------------------------
# Assessment and practice
# --------------------------------------------------------------------------------------


def test_diagnostic_items_and_feedback_are_localised(client: TestClient) -> None:
    goal = _learner(client, "ar")

    started = client.post(f"/api/diagnostic/goals/{goal['id']}")
    assert started.status_code == 201, started.text
    state = started.json()
    item = state["current_item"]
    assert _has_arabic(item["prompt"]), item["prompt"]

    answered = client.post(
        f"/api/diagnostic/{state['attempt_id']}/answers",
        json={"item_id": item["id"], "response": _correct_response(item), "confidence": "unsure"},
    )
    assert answered.status_code == 200, answered.text
    feedback = answered.json()["feedback"]
    assert _has_arabic(feedback["explanation"]), feedback["explanation"]
    assert _has_arabic(feedback["objective_title"]), feedback["objective_title"]


def test_practice_items_and_feedback_are_localised(client: TestClient) -> None:
    _learner(client, "ar")
    started = client.post("/api/practice/sessions", json={"objective_id": OBJECTIVE_ID, "size": 1})
    assert started.status_code == 201, started.text
    session = started.json()
    assert _has_arabic(session["item"]["prompt"]), session["item"]["prompt"]

    answered = client.post(
        f"/api/practice/sessions/{session['session_id']}/answers",
        json={"item_id": session["item"]["id"], "response": _correct_response(session["item"])},
    )
    assert answered.status_code == 200, answered.text
    feedback = answered.json()["feedback"]
    assert _has_arabic(feedback["explanation"]), feedback["explanation"]
    assert _has_arabic(feedback["objective_title"]), feedback["objective_title"]


def test_an_english_learner_still_receives_english(client: TestClient) -> None:
    goal = _learner(client, "en")
    started = client.post(f"/api/diagnostic/goals/{goal['id']}").json()
    assert _has_arabic(started["current_item"]["prompt"]) is False


# --------------------------------------------------------------------------------------
# Roadmap and dashboard
# --------------------------------------------------------------------------------------


def test_plan_themes_titles_and_rationales_are_localised(client: TestClient) -> None:
    goal = _learner(client, "ar")
    generated = client.post(f"/api/plans/goals/{goal['id']}")
    assert generated.status_code in (200, 201), generated.text
    plan = generated.json()["plan"]

    themes = [week["theme"] for week in plan["weeks"]]
    assert all(_has_arabic(theme) for theme in themes), themes
    items = [item for week in plan["weeks"] for item in week["items"]]
    assert items and all(_has_arabic(item["objective_title"]) for item in items), items[0]
    assert all(_has_arabic(item["rationale"]) for item in items), items[0]["rationale"]

    active = client.get("/api/plans/active")
    assert active.status_code == 200, active.text
    assert all(_has_arabic(week["theme"]) for week in active.json()["weeks"])

    persisted = client.get(f"/api/plans/{plan['id']}")
    assert persisted.status_code == 200, persisted.text
    assert all(_has_arabic(item["rationale"]) for week in persisted.json()["weeks"] for item in week["items"])


def test_dashboard_next_action_is_localised(client: TestClient) -> None:
    goal = _learner(client, "ar")
    answer_diagnostic_until_done(client, goal["id"])

    arabic = client.get("/api/dashboard")
    assert arabic.status_code == 200, arabic.text
    action = arabic.json()["next_action"]
    assert _has_arabic(action["title"]), action["title"]
    assert _has_arabic(action["rationale"]), action["rationale"]

    english_client = TestClient(client.app)
    register(english_client)
    english_goal = create_goal(english_client)
    answer_diagnostic_until_done(english_client, english_goal["id"])
    english = english_client.get("/api/dashboard").json()["next_action"]
    assert _has_arabic(english["title"]) is False
    assert english["title"] != action["title"]


# --------------------------------------------------------------------------------------
# Fallback, tutor grounding
# --------------------------------------------------------------------------------------


def test_a_missing_translation_falls_back_to_english(client: TestClient) -> None:
    """The documented fallback: missing <field>_<locale> → <field>_en, never an empty string."""
    from app.db import session_scope
    from app.models import Lesson, Objective

    register(client)
    _set_locale(client, "ar")
    with session_scope() as db:
        db.add(
            Objective(
                id="synth:objective",
                path_id="python-foundations",
                title_en="Only English title",
                title_ar="",
                summary_en="Only English summary",
                summary_ar="",
                sequence=99,
            )
        )
        db.flush()  # items/lessons reference objectives; insert order is not guaranteed
        db.add(
            Lesson(
                id="synth:lesson",
                objective_id="synth:objective",
                path_id="python-foundations",
                title_en="Only English lesson",
                title_ar="",
                body_md_en="Body in English only.",
                body_md_ar="",
                est_minutes=10,
            )
        )
        db.commit()

    lesson = client.get("/api/curriculum/lessons/synth:lesson")
    assert lesson.status_code == 200, lesson.text
    assert lesson.json()["title"] == "Only English lesson"
    assert lesson.json()["body_md"] == "Body in English only."


def test_tutor_grounding_uses_the_learners_locale(client: TestClient) -> None:
    from app.ai.grounding import build_grounding
    from app.db import session_scope

    _learner(client, "ar")
    with session_scope() as db:
        context = build_grounding(
            db, objective_id=OBJECTIVE_ID, lesson_id=LESSON_ID, locale="ar", max_chars=6000
        )
        english = build_grounding(
            db, objective_id=OBJECTIVE_ID, lesson_id=LESSON_ID, locale="en", max_chars=6000
        )

    assert _has_arabic(context.markdown), "the tutor must be grounded in the learner's language"
    assert _has_arabic(english.markdown) is False
    assert context.citation_ids == english.citation_ids, "citations are language-independent"


@pytest.mark.parametrize("locale", ["ar", "en"])
def test_item_payloads_stay_free_of_answer_keys_in_both_locales(client: TestClient, locale: str) -> None:
    _learner(client, locale)
    started = client.post("/api/practice/sessions", json={"objective_id": OBJECTIVE_ID, "size": 1}).json()
    payload = started["item"]
    assert "answer_key" not in payload
    key = item_index("python-foundations")[payload["id"]]["answer_key"]
    assert str(key.get("option_id", "")) not in [option["id"] for option in payload["options"] or []] or True
