from app.core.config import Settings
from app.gateway.registry import ModelRegistry
from app.gateway.router import ModelRouter
from app.schemas.requests import RoutingStrategy


def _router() -> ModelRouter:
    settings = Settings()
    registry = ModelRegistry(settings)
    registry.load()
    return ModelRouter(settings, registry)


def test_lowest_cost_strategy_selects_eligible_model() -> None:
    decision = _router().route(
        requested_model="auto",
        strategy=RoutingStrategy.lowest_cost,
        capability="text-generation",
        estimated_prompt_tokens=12,
    )

    assert decision.model.model_id in {"distilgpt2", "google/flan-t5-small"}
    assert decision.score <= 0


def test_embeddings_route_selects_embedding_model() -> None:
    decision = _router().route(
        requested_model="auto",
        strategy=RoutingStrategy.balanced,
        capability="embeddings",
        estimated_prompt_tokens=8,
    )

    assert decision.model.model_id == "sentence-transformers/all-MiniLM-L6-v2"

