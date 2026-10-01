"""Optional Hugging Face provider.

The implementation imports heavy dependencies lazily so the gateway can run in
mock/local-demo mode without downloading models.
"""

import asyncio
from functools import partial

from app.providers.base import EmbeddingResult, GenerationResult, ModelProvider
from app.providers.mock import estimate_tokens


class HuggingFaceProvider(ModelProvider):
    """Provider backed by Hugging Face Transformers pipelines."""

    provider_name = "huggingface"

    def __init__(self) -> None:
        self._pipelines: dict[str, object] = {}
        self._embedding_models: dict[str, object] = {}

    async def generate(
        self,
        model_id: str,
        prompt: str,
        *,
        temperature: float,
        max_tokens: int,
        top_p: float,
    ) -> GenerationResult:
        pipeline = await self._get_generation_pipeline(model_id)
        call = partial(
            pipeline,
            prompt,
            max_new_tokens=max_tokens,
            do_sample=temperature > 0,
            temperature=max(temperature, 0.01),
            top_p=top_p,
        )
        output = await asyncio.to_thread(call)
        text = _extract_text(output)
        return GenerationResult(
            text=text,
            prompt_tokens=estimate_tokens(prompt),
            completion_tokens=estimate_tokens(text),
            token_counts_estimated=True,
            metadata={"provider_mode": "huggingface"},
        )

    async def embeddings(self, model_id: str, inputs: list[str]) -> EmbeddingResult:
        model = await self._get_embedding_model(model_id)
        embeddings = await asyncio.to_thread(lambda: model.encode(inputs).tolist())
        return EmbeddingResult(
            embeddings=embeddings,
            prompt_tokens=sum(estimate_tokens(text) for text in inputs),
            token_counts_estimated=True,
            metadata={"provider_mode": "huggingface"},
        )

    async def health_check(self, model_id: str) -> bool:
        return bool(model_id)

    async def _get_generation_pipeline(self, model_id: str) -> object:
        if model_id not in self._pipelines:
            from transformers import pipeline

            task = "text2text-generation" if "t5" in model_id.lower() else "text-generation"
            self._pipelines[model_id] = await asyncio.to_thread(pipeline, task, model=model_id)
        return self._pipelines[model_id]

    async def _get_embedding_model(self, model_id: str) -> object:
        if model_id not in self._embedding_models:
            from sentence_transformers import SentenceTransformer

            self._embedding_models[model_id] = await asyncio.to_thread(
                SentenceTransformer,
                model_id,
            )
        return self._embedding_models[model_id]


def _extract_text(output: object) -> str:
    if isinstance(output, list) and output and isinstance(output[0], dict):
        first = output[0]
        return str(first.get("generated_text") or first.get("summary_text") or first)
    return str(output)

