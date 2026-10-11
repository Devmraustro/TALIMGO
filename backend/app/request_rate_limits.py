"""Durable per-learner limit for authenticated mutating API requests.

The UTC fixed-window counter lives on the owning user row. A conditional UPDATE both checks the
current count and increments/resets it atomically, so concurrent requests and multiple workers share
the same limit. Claims are committed in a dedicated session and never rolled back with the request.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import case, or_, update

from app.db import session_scope
from app.models import User
from app.utils import utcnow


class WriteRateLimitExceeded(RuntimeError):
    """An authenticated learner exceeded the mutating-request budget for this minute."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = max(1, retry_after)
        super().__init__("Authenticated write rate limit reached.")


def reserve_write_request_committed(user_id: str, *, limit: int, now: datetime | None = None) -> int:
    """Atomically claim one write in the current UTC minute and commit it independently.

    Window rollover and increment are one UPDATE against the old row values. This avoids the
    read-then-write race and needs no per-window row/table cleanup. Only authenticated mutating
    routes call this function; login attempts have their separate existing policy.
    """
    if limit < 1:
        raise ValueError("The write-request limit must be positive.")

    moment = now or utcnow()
    epoch_seconds = int(moment.timestamp())
    window = epoch_seconds // 60
    retry_after = 60 - (epoch_seconds % 60)

    with session_scope() as db:
        previous_window = User.write_rate_window < window
        result = db.execute(
            update(User)
            .where(
                User.id == user_id,
                or_(previous_window, User.write_rate_count < limit),
            )
            .values(
                write_rate_window=case(
                    (previous_window, window),
                    else_=User.write_rate_window,
                ),
                write_rate_count=case(
                    (previous_window, 1),
                    else_=User.write_rate_count + 1,
                ),
            )
        )
        if result.rowcount != 1:
            raise WriteRateLimitExceeded(retry_after)
        db.commit()
        return 1
