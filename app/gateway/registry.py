"""Phase 1 model registry loader.

The full registry abstraction is expanded in Phase 3. This implementation keeps
the API routes useful immediately by loading model metadata from YAML.
"""

from pydantic import TypeAdapter

from app.core.config import Settings, load_yaml_file
from app.schemas.models import ModelMetadata


class ModelRegistry:
    """Read-only model registry backed by YAML configuration."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._models: dict[str, ModelMetadata] = {}

    def load(self) -> None:
        data = load_yaml_file(self._settings.models_config_path)
        adapter = TypeAdapter(list[ModelMetadata])
        models = adapter.validate_python(data.get("models", []))
        self._models = {model.model_id: model for model in models}

    def list_models(self) -> list[ModelMetadata]:
        if not self._models:
            self.load()
        return list(self._models.values())

    def get_model(self, model_id: str) -> ModelMetadata | None:
        if not self._models:
            self.load()
        return self._models.get(model_id)

    def set_availability(self, model_id: str, availability: str) -> ModelMetadata | None:
        model = self.get_model(model_id)
        if model is None:
            return None
        updated = model.model_copy(update={"availability": availability})
        self._models[model_id] = updated
        return updated

    def has_healthy_model(self) -> bool:
        return any(
            model.availability == "enabled" and model.health_status != "UNHEALTHY"
            for model in self.list_models()
        )
