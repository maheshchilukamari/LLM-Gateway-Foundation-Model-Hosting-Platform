from app.cache.keys import stable_cache_key
from app.cache.memory_cache import MemoryCache


def test_stable_cache_key_is_order_independent() -> None:
    left = stable_cache_key("test", {"a": 1, "b": 2})
    right = stable_cache_key("test", {"b": 2, "a": 1})

    assert left == right


async def test_memory_cache_round_trip() -> None:
    cache = MemoryCache()

    await cache.set("key", "value", ttl_seconds=60)

    assert await cache.get("key") == "value"
    assert cache.size() == 1

