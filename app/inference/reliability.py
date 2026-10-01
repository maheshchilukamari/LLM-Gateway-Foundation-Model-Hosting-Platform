"""Reliability primitives: retries and circuit breakers."""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from time import monotonic
from typing import TypeVar

T = TypeVar("T")


class CircuitState(StrEnum):
    closed = "CLOSED"
    open = "OPEN"
    half_open = "HALF_OPEN"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_seconds: float = 30.0
    state: CircuitState = CircuitState.closed
    failure_count: int = 0
    opened_at: float | None = None

    def allow_request(self) -> bool:
        if self.state == CircuitState.closed:
            return True
        if self.state == CircuitState.open and self.opened_at is not None:
            if monotonic() - self.opened_at >= self.recovery_seconds:
                self.state = CircuitState.half_open
                return True
        return self.state == CircuitState.half_open

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None
        self.state = CircuitState.closed

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.open
            self.opened_at = monotonic()


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 2,
    base_delay_seconds: float = 0.05,
) -> T:
    last_error: Exception | None = None
    for index in range(attempts):
        try:
            return await operation()
        except Exception as exc:
            last_error = exc
            if index < attempts - 1:
                await asyncio.sleep(base_delay_seconds * (2**index))
    if last_error is None:
        raise RuntimeError("retry operation failed without exception")
    raise last_error

