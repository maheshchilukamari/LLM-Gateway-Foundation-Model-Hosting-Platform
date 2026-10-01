"""Dynamic model routing strategies."""

from dataclasses import dataclass
from typing import Any

from app.core.config import Settings, load_yaml_file
from app.core.exceptions import RoutingError
from app.gateway.registry import ModelRegistry
from app.schemas.models import ModelAvailability, ModelHealthStatus, ModelMetadata
from app.schemas.requests import RoutingStrategy


@dataclass(frozen=True)
class RoutingDecision:
    """Selected model and scoring explanation."""

    model: ModelMetadata
    strategy: RoutingStrategy
    score: float
    candidates_considered: int
    reason: str


class ModelRouter:
    """Select models based on configured routing strategies."""

    def __init__(self, settings: Settings, registry: ModelRegistry) -> None:
        self._settings = settings
        self._registry = registry
        self._routing_config = load_yaml_file(settings.routing_config_path).get("routing", {})

    def route(
        self,
        *,
        requested_model: str,
        strategy: RoutingStrategy,
        capability: str,
        estimated_prompt_tokens: int,
        resource_snapshot: dict[str, float] | None = None,
    ) -> RoutingDecision:
        candidates = self._eligible_models(requested_model, capability, estimated_prompt_tokens)
        if not candidates:
            raise RoutingError(
                f"No eligible models for requested_model={requested_model}, capability={capability}"
            )

        scored = [
            (
                self._score_model(strategy, model, candidates, resource_snapshot or {}),
                model,
            )
            for model in candidates
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        score, model = scored[0]
        return RoutingDecision(
            model=model,
            strategy=strategy,
            score=round(score, 6),
            candidates_considered=len(candidates),
            reason=f"selected by {strategy}",
        )

    def fallback_chain(self, model_id: str) -> list[str]:
        chains = self._routing_config.get("fallback_chains", {})
        configured = chains.get(model_id, [])
        return [model_id, *configured]

    def _eligible_models(
        self,
        requested_model: str,
        capability: str,
        estimated_prompt_tokens: int,
    ) -> list[ModelMetadata]:
        if requested_model != "auto":
            model = self._registry.get_model(requested_model)
            if model and self._is_eligible(model, capability, estimated_prompt_tokens):
                return [model]
            return []

        return [
            model
            for model in self._registry.list_models()
            if self._is_eligible(model, capability, estimated_prompt_tokens)
        ]

    def _is_eligible(
        self,
        model: ModelMetadata,
        capability: str,
        estimated_prompt_tokens: int,
    ) -> bool:
        if model.availability != ModelAvailability.enabled:
            return False
        if model.health_status == ModelHealthStatus.unhealthy:
            return False
        if capability not in model.supported_capabilities and model.task_type != capability:
            return False
        max_utilization = self._routing_config.get("constraints", {}).get(
            "max_context_utilization",
            0.9,
        )
        return estimated_prompt_tokens <= int(model.context_window * max_utilization)

    def _score_model(
        self,
        strategy: RoutingStrategy,
        model: ModelMetadata,
        candidates: list[ModelMetadata],
        resource_snapshot: dict[str, float],
    ) -> float:
        if strategy == RoutingStrategy.lowest_latency:
            return -model.average_latency_ms
        if strategy == RoutingStrategy.lowest_cost:
            return -model.estimated_cost_per_1k_tokens
        if strategy == RoutingStrategy.highest_quality:
            return model.quality_score
        if strategy == RoutingStrategy.highest_throughput:
            return model.throughput_score
        if strategy == RoutingStrategy.resource_aware:
            return self._balanced_score(model, candidates, "resource_aware", resource_snapshot)
        return self._balanced_score(model, candidates, "balanced", resource_snapshot)

    def _balanced_score(
        self,
        model: ModelMetadata,
        candidates: list[ModelMetadata],
        strategy_name: str,
        resource_snapshot: dict[str, float],
    ) -> float:
        weights: dict[str, Any] = self._routing_config.get("strategies", {}).get(strategy_name, {})
        quality = model.quality_score
        latency = _normalize_lower_is_better(
            model.average_latency_ms,
            [m.average_latency_ms for m in candidates],
        )
        cost = _normalize_lower_is_better(
            model.estimated_cost_per_1k_tokens,
            [m.estimated_cost_per_1k_tokens for m in candidates],
        )
        throughput = model.throughput_score
        cpu_penalty = resource_snapshot.get("cpu_percent", 0.0) / 100.0
        memory_penalty = resource_snapshot.get("memory_percent", 0.0) / 100.0
        return (
            weights.get("quality_weight", 0.4) * quality
            + weights.get("latency_weight", 0.25) * latency
            + weights.get("cost_weight", 0.2) * cost
            + weights.get("throughput_weight", 0.15) * throughput
            - weights.get("cpu_weight", 0.0) * cpu_penalty
            - weights.get("memory_weight", 0.0) * memory_penalty
        )


def _normalize_lower_is_better(value: float, values: list[float]) -> float:
    low = min(values)
    high = max(values)
    if high == low:
        return 1.0
    return 1.0 - ((value - low) / (high - low))
