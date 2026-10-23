"""Quota durability across every tutor failure path, through the real tutor API.

The bug these tests lock out: the allowance was claimed on the *request* session, which the router
only commits after a fully validated reply has been stored. Any failure after the claim therefore
ended in ``Session.close()`` — a rollback — so a failed request silently handed the slot back, and
the documented policy ("an attempted request counts") was untrue.

Each case drives the real HTTP endpoint with a mocked **local** transport, then asserts three things:
the learner-visible status, that no tutor exchange was stored, and that the usage endpoint reports the
consumed slot. With a limit of one, the follow-up request must be refused with 429.
"""

from __future__ import annotations

import json

import httpx
import pytest

from app.ai.adapter import LocalModelClient
from app.db import session_scope
from app.models import TutorMessage, TutorThread
from tests.conftest import register

OBJECTIVE = "py:values"
QUESTION = "Why is 7 / 2 a float?"

VALID_REPLY = {
    "reply": "In Python 3, / always produces a float, so 7 / 2 is 3.5.",
    "hint_level": 1,
    "citations": [f"objective:{OBJECTIVE}"],
    "confidence": "high",
    "follow_up_question": "What does 7 // 2 print?",
}


def _client_with_transport(ai_client_factory, monkeypatch, handler, **extra):
    client = ai_client_factory(TALIMGO_AI_MODEL="local-test-model", **extra)
    monkeypatch.setattr(
        "app.ai.tutor.LocalModelClient",
        lambda settings: LocalModelClient(settings, transport=httpx.MockTransport(handler)),
    )
    return client


def _reply_handler(payload: dict):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"model": "local-test-model", "message": {"content": json.dumps(payload)}}
        )

    return handler


def _unreachable(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("connection refused", request=request)


def _http_error(request: httpx.Request) -> httpx.Response:
    # An error body that must never reach the learner, including a credential-shaped string.
    return httpx.Response(500, text="upstream exploded: token=sk-not-a-real-key-000000000000")


def _not_json(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, text="<html>this is not a completion</html>")


def _empty_completion(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"model": "local-test-model", "message": {"content": "   "}})


def _rejected_schema(request: httpx.Request) -> httpx.Response:
    # Well-formed JSON for the transport, unusable for TALIMGO: the citation is not in the context.
    payload = {**VALID_REPLY, "citations": ["objective:not-in-context"]}
    return httpx.Response(
        200, json={"model": "local-test-model", "message": {"content": json.dumps(payload)}}
    )


def _rejected_policy(request: httpx.Request) -> httpx.Response:
    payload = {**VALID_REPLY, "reply": "Finish this and we guarantee you a job in three months."}
    return httpx.Response(
        200, json={"model": "local-test-model", "message": {"content": json.dumps(payload)}}
    )


FAILURE_PATHS = [
    ("runtime_unavailable", _unreachable, 503),
    ("runtime_http_error", _http_error, 502),
    ("non_json_output", _not_json, 502),
    ("empty_completion", _empty_completion, 502),
    ("rejected_citation", _rejected_schema, 502),
    ("rejected_prohibited_claim", _rejected_policy, 502),
]


def _stored_exchange_count() -> tuple[int, int]:
    with session_scope() as db:
        return db.query(TutorThread).count(), db.query(TutorMessage).count()


@pytest.mark.parametrize(
    ("case", "handler", "expected_status"), FAILURE_PATHS, ids=[case[0] for case in FAILURE_PATHS]
)
def test_a_failing_request_consumes_its_slot_and_stores_nothing(
    ai_client_factory, monkeypatch, case: str, handler, expected_status: int
) -> None:
    client = _client_with_transport(
        ai_client_factory, monkeypatch, handler, TALIMGO_AI_DAILY_REQUESTS_PER_LEARNER=1
    )
    register(client)

    before_threads, before_messages = _stored_exchange_count()
    response = client.post("/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": QUESTION})

    assert response.status_code == expected_status, f"{case}: {response.text}"
    # 4. Unvalidated exchanges are never persisted, and no thread is created for a failed attempt.
    assert _stored_exchange_count() == (before_threads, before_messages), f"{case}: stored something"
    assert client.get("/api/tutor/threads").json() == []

    # 3. The reserved slot survives the failure: the usage endpoint reports it as consumed.
    usage = client.get("/api/tutor/usage").json()
    assert usage["used_today"] == 1, f"{case}: the reservation was rolled back"
    assert usage["daily_limit"] == 1

    # And the allowance is genuinely exhausted for the rest of the day.
    follow_up = client.post(
        "/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": "Another question"}
    )
    assert follow_up.status_code == 429, f"{case}: {follow_up.text}"
    assert client.get("/api/tutor/usage").json()["used_today"] == 1


LEAKY_FRAGMENTS = (
    "sk-not-a-real-key",
    "upstream exploded",
    "Traceback",
    "httpx",
    "11434",  # the configured endpoint address is internal detail
    "ConnectError",
    "RuntimeError",
)


def _assert_no_internal_detail(detail: str) -> None:
    for fragment in LEAKY_FRAGMENTS:
        assert fragment not in detail, f"{fragment!r} leaked to the learner: {detail}"
    assert "127.0.0.1" not in detail and "localhost" not in detail


def test_the_learner_never_sees_the_upstream_error_body_or_a_traceback(
    ai_client_factory, monkeypatch
) -> None:
    client = _client_with_transport(ai_client_factory, monkeypatch, _http_error)
    register(client)

    response = client.post("/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": QUESTION})
    assert response.status_code == 502
    detail = response.json()["detail"]
    _assert_no_internal_detail(detail)
    # The sentence is stable and actionable, and it states the consumed-slot policy honestly.
    assert detail.startswith("The local model returned a response TALIMGO could not use")
    assert "still counts" in detail


def test_the_unavailable_sentence_is_equally_free_of_internal_detail(ai_client_factory, monkeypatch) -> None:
    client = _client_with_transport(ai_client_factory, monkeypatch, _unreachable)
    register(client)

    response = client.post("/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": QUESTION})
    assert response.status_code == 503
    detail = response.json()["detail"]
    _assert_no_internal_detail(detail)
    assert "unavailable" in detail.lower() and "local" in detail.lower()


def test_a_successful_request_consumes_exactly_one_slot(ai_client_factory, monkeypatch) -> None:
    """The control case: durability of the claim must not double-count or lose the happy path."""
    client = _client_with_transport(
        ai_client_factory,
        monkeypatch,
        _reply_handler(VALID_REPLY),
        TALIMGO_AI_DAILY_REQUESTS_PER_LEARNER=2,
    )
    register(client)

    first = client.post("/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": QUESTION})
    assert first.status_code == 200, first.text
    assert client.get("/api/tutor/usage").json()["used_today"] == 1
    assert first.json()["validation"]["usage_today"] == 1, "one request, one unit"

    second = client.post("/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": QUESTION})
    assert second.status_code == 200, second.text
    assert client.get("/api/tutor/usage").json()["used_today"] == 2

    threads = client.get("/api/tutor/threads").json()
    assert len(threads) == 1, "the same objective continues one thread"
    assert [message["role"] for message in threads[0]["messages"]] == [
        "learner",
        "tutor",
        "learner",
        "tutor",
    ]


def test_a_rejected_request_that_costs_nothing_still_costs_no_quota(ai_client_factory, monkeypatch) -> None:
    """Consent, objective and grounding checks run *before* the claim (P1 requirement 1)."""
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _reply_handler(VALID_REPLY)(request)

    client = _client_with_transport(ai_client_factory, monkeypatch, handler)
    register(client)

    unknown = client.post("/api/tutor/ask", json={"objective_id": "py:nope", "question": QUESTION})
    assert unknown.status_code == 404

    mismatched = client.post(
        "/api/tutor/ask",
        json={
            "objective_id": OBJECTIVE,
            "lesson_id": "py:conditionals:lesson",
            "question": QUESTION,
        },
    )
    assert mismatched.status_code == 400, mismatched.text

    assert calls == [], "refused requests must never reach the local model"
    assert client.get("/api/tutor/usage").json()["used_today"] == 0

    # The allowance is therefore intact for a request that can actually be served.
    allowed = client.post("/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": QUESTION})
    assert allowed.status_code == 200, allowed.text


def test_consent_refusal_consumes_no_quota(ai_client_factory, monkeypatch) -> None:
    client = _client_with_transport(ai_client_factory, monkeypatch, _reply_handler(VALID_REPLY))
    register(client, ai_consent=False)

    refused = client.post("/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": QUESTION})
    assert refused.status_code == 403
    assert client.get("/api/tutor/usage").json()["used_today"] == 0


def test_concurrent_tutor_requests_cannot_exceed_the_limit(ai_client_factory, monkeypatch) -> None:
    """Two concurrent requests, one slot: exactly one may reach the model."""
    import threading
    import time

    from fastapi.testclient import TestClient

    reached: list[str] = []
    lock = threading.Lock()

    def handler(request: httpx.Request) -> httpx.Response:
        with lock:
            reached.append("call")
        time.sleep(0.3)  # keep the model call in flight while the other request arrives
        return _reply_handler(VALID_REPLY)(request)

    client = _client_with_transport(
        ai_client_factory,
        monkeypatch,
        handler,
        TALIMGO_AI_DAILY_REQUESTS_PER_LEARNER=1,
    )
    register(client)
    cookies = dict(client.cookies)

    # A second client over the same app and database, with the first learner's session cookie: the
    # two requests then interleave the way two browser tabs would.
    other = TestClient(client.app)
    other.cookies.update(cookies)

    results: dict[str, int] = {}
    barrier = threading.Barrier(2)

    def ask(name: str, target: TestClient) -> None:
        barrier.wait()
        response = target.post("/api/tutor/ask", json={"objective_id": OBJECTIVE, "question": QUESTION})
        with lock:
            results[name] = response.status_code

    threads = [
        threading.Thread(target=ask, args=("first", client)),
        threading.Thread(target=ask, args=("second", other)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    statuses = sorted(results.values())
    assert statuses == [200, 429], f"expected exactly one served request, got {statuses}"
    assert len(reached) == 1, f"the local model must be called once, was called {len(reached)} times"
    assert client.get("/api/tutor/usage").json()["used_today"] == 1
