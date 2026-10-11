"""Process-wide model-generation gate: bounded waiting, release semantics and API mapping."""

from __future__ import annotations

import threading
import time

import pytest

from app.ai.tutor import AiBusyError, model_slot
from tests.conftest import register


def test_model_gate_rejects_when_the_only_slot_is_occupied() -> None:
    entered = threading.Event()
    release = threading.Event()

    def hold_slot() -> None:
        with model_slot(limit=1, wait_seconds=1.0):
            entered.set()
            release.wait(timeout=2.0)

    worker = threading.Thread(target=hold_slot)
    worker.start()
    try:
        assert entered.wait(timeout=1.0), "worker never acquired the model slot"
        started = time.monotonic()
        with pytest.raises(AiBusyError), model_slot(limit=1, wait_seconds=0.02):
            pytest.fail("a second generation entered an occupied slot")
        assert time.monotonic() - started < 0.5, "the queue wait must remain bounded"
    finally:
        release.set()
        worker.join(timeout=2.0)
    assert not worker.is_alive(), "the slot holder should have exited"
    # The slot is released even after contention.
    with model_slot(limit=1, wait_seconds=0.02):
        pass


def test_model_gate_releases_after_generation_raises() -> None:
    with pytest.raises(RuntimeError, match="synthetic runtime failure"), model_slot(
        limit=1, wait_seconds=0.02
    ):
        raise RuntimeError("synthetic runtime failure")
    with model_slot(limit=1, wait_seconds=0.02):
        pass


def test_busy_tutor_request_does_not_consume_daily_allowance(
    ai_client_factory, monkeypatch
) -> None:
    client = ai_client_factory(TALIMGO_AI_MAX_CONCURRENT_REQUESTS=1)
    register(client)

    def saturated_slot(*, limit: int, wait_seconds: float):
        raise AiBusyError(retry_after=1)

    monkeypatch.setattr("app.ai.tutor.model_slot", saturated_slot)
    response = client.post(
        "/api/tutor/ask",
        json={"objective_id": "py:values", "question": "Explain values"},
    )
    assert response.status_code == 503, response.text
    assert response.headers["Retry-After"] == "1"
    assert "did not consume" in response.json()["detail"]
    assert client.get("/api/tutor/usage").json()["used_today"] == 0
    assert client.get("/api/tutor/threads").json() == []
