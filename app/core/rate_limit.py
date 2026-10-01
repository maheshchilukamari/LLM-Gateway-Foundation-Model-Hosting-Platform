"""Simple in-memory API-key rate limiter."""

from collections import defaultdict, deque
from time import monotonic
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


class InMemoryRateLimiter:
    """Per-key sliding-window request limiter."""

    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, *, limit: int, window_seconds: int = 60) -> bool:
        now = monotonic()
        bucket = self._requests[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True


rate_limiter = InMemoryRateLimiter()


async def enforce_rate_limit(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    settings = get_settings()
    key = x_api_key or "anonymous"
    if not rate_limiter.allow(key, limit=settings.rate_limit_requests_per_minute):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
