"""Tiny in-process sliding-window rate limiter.

Fine for a single-node deployment (our target). If this ever runs multi-node,
swap the backing store for Redis behind the same ``hit`` signature.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

_lock = threading.Lock()
_events: dict[str, deque[float]] = defaultdict(deque)


def hit(key: str, limit: int, window_seconds: int, *, now: float | None = None) -> bool:
    """Record an attempt for ``key``. Return True if it is allowed, False if over limit."""
    ts = now if now is not None else time.time()
    cutoff = ts - window_seconds
    with _lock:
        q = _events[key]
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(ts)
        return True


def seconds_until_next(
    key: str, limit: int, window_seconds: int, *, now: float | None = None
) -> int:
    ts = now if now is not None else time.time()
    with _lock:
        q = _events.get(key)
        if not q or len(q) < limit:
            return 0
        return max(0, int(q[0] + window_seconds - ts) + 1)


def reset() -> None:
    """Test helper."""
    with _lock:
        _events.clear()
