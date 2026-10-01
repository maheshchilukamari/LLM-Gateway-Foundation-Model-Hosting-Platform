"""Common provider interfaces for foundation model execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GenerationResult:
    """Normalized text generation result returned by providers."""

    text: str
    prompt_tokens: int
    completion_tokens: int
    token_counts_estimated: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class EmbeddingResult:
    """Normalized embedding result returned by providers."""

    embeddings: list[list[float]]
    prompt_tokens: int
    token_counts_estimated: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelProvider(ABC):
    """Provider boundary for local or remote model serving backends."""

    provider_name: str

    @abstractmethod
    async def generate(
        self,
        model_id: str,
        prompt: str,
        *,
        temperature: float,
        max_tokens: int,
        top_p: float,
    ) -> GenerationResult:
        """Generate text for a prompt."""

    @abstractmethod
    async def embeddings(self, model_id: str, inputs: list[str]) -> EmbeddingResult:
        """Generate embeddings for one or more inputs."""

    @abstractmethod
    async def health_check(self, model_id: str) -> bool:
        """Return whether the provider can serve the model."""

    async def load_model(self, model_id: str) -> None:
        """Load a model into memory when the provider supports explicit loading."""
        return None

    async def unload_model(self, model_id: str) -> None:
        """Unload a model when the provider supports explicit unloading."""
        return None
