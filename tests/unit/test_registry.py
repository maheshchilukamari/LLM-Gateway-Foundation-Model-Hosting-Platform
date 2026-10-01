from app.core.config import Settings
from app.gateway.registry import ModelRegistry


def test_registry_loads_models_from_yaml() -> None:
    registry = ModelRegistry(Settings())
    registry.load()

    models = registry.list_models()

    assert {model.model_id for model in models} >= {
        "distilgpt2",
        "google/flan-t5-small",
        "sentence-transformers/all-MiniLM-L6-v2",
    }
    assert registry.has_healthy_model()


def test_registry_returns_none_for_unknown_model() -> None:
    registry = ModelRegistry(Settings())

    assert registry.get_model("missing-model") is None

