"""Cache interfaces."""

from abc import ABC, abstractmethod


class CacheBackend(ABC):
    """Async cache backend boundary."""

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """Return a cached serialized value."""

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        """Store a serialized value with TTL."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return whether the cache backend is available."""

