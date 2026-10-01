"""Simple batching abstraction."""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class BatchingConfig:
    enabled: bool = False
    max_batch_size: int = 4
    max_wait_ms: int = 25


class SimpleBatcher:
    """Minimal async batching helper for compatible same-model work."""

    def __init__(self, config: BatchingConfig) -> None:
        self._config = config

    async def run(
        self,
        items: list[T],
        handler: Callable[[list[T]], Awaitable[list[R]]],
    ) -> list[R]:
        if not self._config.enabled or len(items) <= 1:
            return await handler(items)
        await asyncio.sleep(self._config.max_wait_ms / 1000)
        return await handler(items[: self._config.max_batch_size])

