"""Redis cache backend with graceful optional dependency handling."""

from app.cache.base import CacheBackend


class RedisCache(CacheBackend):
    """Async Redis cache backend."""

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._client: object | None = None

    async def _connect(self) -> object:
        if self._client is None:
            import redis.asyncio as redis

            self._client = redis.from_url(self._redis_url, decode_responses=True)
        return self._client

    async def get(self, key: str) -> str | None:
        client = await self._connect()
        return await client.get(key)  # type: ignore[attr-defined]

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        client = await self._connect()
        await client.setex(key, ttl_seconds, value)  # type: ignore[attr-defined]

    async def health_check(self) -> bool:
        try:
            client = await self._connect()
            return bool(await client.ping())  # type: ignore[attr-defined]
        except Exception:
            return False

