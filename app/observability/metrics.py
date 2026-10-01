"""Prometheus metrics setup."""

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST
from starlette.responses import Response

REQUESTS_TOTAL = Counter(
    "llm_requests_total",
    "Total LLM gateway requests.",
    ["endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "llm_request_latency_seconds",
    "Gateway request latency in seconds.",
    ["endpoint"],
)

ACTIVE_REQUESTS = Gauge(
    "llm_active_requests",
    "Current active gateway requests.",
)

INFERENCE_LATENCY = Histogram(
    "llm_inference_latency_seconds",
    "Provider inference latency in seconds.",
    ["model", "provider"],
)

CACHE_HITS = Counter(
    "llm_cache_hits_total",
    "Total cache hits.",
    ["endpoint"],
)

CACHE_MISSES = Counter(
    "llm_cache_misses_total",
    "Total cache misses.",
    ["endpoint"],
)

TOKENS_GENERATED = Counter(
    "llm_tokens_generated_total",
    "Generated completion tokens.",
    ["model"],
)

PROMPT_TOKENS = Counter(
    "llm_prompt_tokens_total",
    "Prompt tokens processed.",
    ["model"],
)

MODEL_REQUESTS = Counter(
    "llm_model_requests_total",
    "Requests served by model.",
    ["model", "provider", "status"],
)

ROUTING_DECISIONS = Counter(
    "llm_routing_decisions_total",
    "Routing decisions by selected model and strategy.",
    ["model", "routing_strategy"],
)

FALLBACK_TOTAL = Counter(
    "llm_fallback_total",
    "Fallback attempts by model.",
    ["model"],
)

MODEL_HEALTH = Gauge(
    "llm_model_health",
    "Model health status as 1 healthy, 0.5 degraded, 0 unhealthy.",
    ["model", "provider"],
)

ESTIMATED_COST = Counter(
    "llm_estimated_cost_total",
    "Estimated request cost.",
    ["model"],
)


async def metrics_response() -> Response:
    """Return Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
