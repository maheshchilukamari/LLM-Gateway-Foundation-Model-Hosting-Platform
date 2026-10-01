"""Deterministic local provider used for tests and lightweight demos."""

import hashlib
import math
from collections import Counter

from app.providers.base import EmbeddingResult, GenerationResult, ModelProvider


def estimate_tokens(text: str) -> int:
    """Cheap token estimate used when a model tokenizer is not available."""
    return max(1, len(text.split()))


class MockProvider(ModelProvider):
    """Small provider that behaves like inference without model downloads."""

    provider_name = "mock"

    async def generate(
        self,
        model_id: str,
        prompt: str,
        *,
        temperature: float,
        max_tokens: int,
        top_p: float,
    ) -> GenerationResult:
        del temperature, top_p
        prompt_tokens = estimate_tokens(prompt)
        prefix = prompt.strip().replace("\n", " ")[:220]
        text = (
            f"[{model_id}] Mock inference response: {prefix}"
            if prefix
            else f"[{model_id}] Mock inference response."
        )
        words = text.split()[:max_tokens]
        generated = " ".join(words)
        return GenerationResult(
            text=generated,
            prompt_tokens=prompt_tokens,
            completion_tokens=estimate_tokens(generated),
            metadata={"provider_mode": "mock"},
        )

    async def embeddings(self, model_id: str, inputs: list[str]) -> EmbeddingResult:
        embeddings = [_hashed_embedding(text) for text in inputs]
        return EmbeddingResult(
            embeddings=embeddings,
            prompt_tokens=sum(estimate_tokens(text) for text in inputs),
            metadata={"provider_mode": "mock", "model_id": model_id},
        )

    async def health_check(self, model_id: str) -> bool:
        return model_id != "unhealthy-model"


def _hashed_embedding(text: str, dimensions: int = 32) -> list[float]:
    """Create a deterministic semantic-ish vector from tokens."""
    counts = Counter(text.lower().split())
    vector = [0.0] * dimensions
    for token, count in counts.items():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = digest[0] % dimensions
        sign = 1.0 if digest[1] % 2 == 0 else -1.0
        vector[index] += sign * count

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]

