# Reliability

Reliability patterns planned for the gateway:

- Request timeouts.
- Retry with exponential backoff.
- Fallback model chains.
- Graceful degradation when Redis is unavailable.
- Concurrency limits.
- Health-aware routing.
- Circuit breaker states: `CLOSED`, `OPEN`, and `HALF_OPEN`.

Failures should be observable through metrics, logs, and traces.

