"""Token and cost accounting helpers."""

from app.schemas.models import ModelMetadata
from app.schemas.responses import TokenUsage


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


def build_usage(
    prompt_tokens: int,
    completion_tokens: int,
    *,
    estimated: bool = True,
) -> TokenUsage:
    return TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        estimated=estimated,
    )


def estimate_cost(model: ModelMetadata, usage: TokenUsage) -> float:
    return round((usage.total_tokens / 1000.0) * model.estimated_cost_per_1k_tokens, 8)
