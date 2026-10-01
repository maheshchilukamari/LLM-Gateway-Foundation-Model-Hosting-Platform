"""Embedding service used by RAG."""

from app.providers.base import ModelProvider


class EmbeddingService:
    """Generate embeddings through the provider interface."""

    def __init__(self, provider: ModelProvider, model_id: str) -> None:
        self._provider = provider
        self._model_id = model_id

    async def embed(self, texts: list[str]) -> list[list[float]]:
        result = await self._provider.embeddings(self._model_id, texts)
        return result.embeddings

