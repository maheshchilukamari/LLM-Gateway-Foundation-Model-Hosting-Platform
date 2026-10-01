"""In-memory TTL cache used for local development and Redis fallback."""

from time import monotonic

from app.cache.base import CacheBackend


class MemoryCache(CacheBackend):
    """Small async-compatible TTL cache."""

    def __init__(self) -> None:
        self._values: dict[str, tuple[float, str]] = {}

    async def get(self, key: str) -> str | None:
        item = self._values.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at < monotonic():
            self._values.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._values[key] = (monotonic() + ttl_seconds, value)

    async def health_check(self) -> bool:
        return True

    def size(self) -> int:
        return len(self._values)

