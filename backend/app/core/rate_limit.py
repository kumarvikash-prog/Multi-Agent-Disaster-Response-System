"""In-memory sliding-window rate limiter.

Designed for the Phase 1 single-instance deployment (no Redis).
This is not safe across multiple processes — documented limit (ADR-0001).

Usage:
    limiter = RateLimiter(max_calls=5, window_seconds=60)
    if not limiter.allow(key="ip:1.2.3.4"):
        raise RateLimitedError(retry_after_seconds=limiter.retry_after(key))
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock


class RateLimiter:
    """A thread-safe in-memory sliding-window rate limiter.

    Args:
        max_calls:       Maximum number of allowed calls within the window.
        window_seconds:  Length of the sliding window in seconds.
    """

    def __init__(self, max_calls: int, window_seconds: int) -> None:
        self._max = max_calls
        self._window = window_seconds
        self._calls: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        """Return True if the call is within the limit; False if rate-limited.

        Always records the attempt regardless of outcome.
        """
        now = time.monotonic()
        cutoff = now - self._window

        with self._lock:
            bucket = self._calls[key]
            # Drop timestamps older than the window
            while bucket and bucket[0] < cutoff:
                bucket.popleft()

            if len(bucket) >= self._max:
                return False

            bucket.append(now)
            return True

    def retry_after(self, key: str) -> int:
        """Return the number of seconds until the oldest call falls out of the window."""
        with self._lock:
            bucket = self._calls.get(key)
            if not bucket:
                return 0
            oldest = bucket[0]
            remaining = int((oldest + self._window) - time.monotonic())
            return max(remaining, 1)

    def reset(self, key: str) -> None:
        """Clear the call history for a key (used in tests)."""
        with self._lock:
            self._calls.pop(key, None)
