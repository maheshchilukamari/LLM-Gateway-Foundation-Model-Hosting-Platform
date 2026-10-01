"""Async inference orchestration for gateway endpoints."""

import asyncio
import json
from time import perf_counter
from typing import Any

from app.cache.base import CacheBackend
from app.cache.keys import stable_cache_key
from app.core.config import Settings
from app.core.exceptions import ModelUnavailableError
from app.gateway.router import ModelRouter, RoutingDecision
from app.governance.lineage import LineageRecord
from app.governance.policies import PolicyEngine
from app.inference.reliability import CircuitBreaker, retry_async
from app.inference.resource_monitor import ResourceMonitor
from app.inference.token_accounting import build_usage, estimate_cost, estimate_tokens
from app.observability.metrics import (
    CACHE_HITS,
    CACHE_MISSES,
    FALLBACK_TOTAL,
    INFERENCE_LATENCY,
    MODEL_REQUESTS,
    ROUTING_DECISIONS,
    TOKENS_GENERATED,
)
from app.providers.factory import ProviderFactory
from app.rag.pipeline import RagPipeline
from app.schemas.requests import (
    ChatCompletionRequest,
    EmbeddingRequest,
    GenerateRequest,
    RagQueryRequest,
    RoutingStrategy,
)
from app.schemas.responses import EmbeddingResponse, GatewayResponse, RagResponse, RagSource


class InferenceEngine:
    """Coordinate validation, routing, caching, provider calls, and lineage."""

    def __init__(
        self,
        *,
        settings: Settings,
        router: ModelRouter,
        provider_factory: ProviderFactory,
        cache: CacheBackend,
        policy_engine: PolicyEngine,
        resource_monitor: ResourceMonitor,
        rag_pipeline: RagPipeline | None = None,
    ) -> None:
        self._settings = settings
        self._router = router
        self._provider_factory = provider_factory
        self._cache = cache
        self._policy_engine = policy_engine
        self._resource_monitor = resource_monitor
        self._rag_pipeline = rag_pipeline
        self._circuits: dict[str, CircuitBreaker] = {}
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
        self.lineage_records: list[LineageRecord] = []

    async def chat(
        self,
        request_id: str,
        payload: ChatCompletionRequest,
        started_at: float,
    ) -> GatewayResponse:
        prompt = _messages_to_prompt(payload.messages)
        return await self._generate_response(
            request_id=request_id,
            started_at=started_at,
            model=payload.model,
            prompt=prompt,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            top_p=payload.top_p,
            routing_strategy=payload.routing_strategy,
            use_rag=payload.use_rag,
            metadata=payload.metadata,
        )

    async def generate(
        self,
        request_id: str,
        payload: GenerateRequest,
        started_at: float,
    ) -> GatewayResponse:
        return await self._generate_response(
            request_id=request_id,
            started_at=started_at,
            model=payload.model,
            prompt=payload.prompt,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            top_p=payload.top_p,
            routing_strategy=payload.routing_strategy,
            use_rag=payload.use_rag,
            metadata=payload.metadata,
        )

    async def embeddings(
        self,
        request_id: str,
        payload: EmbeddingRequest,
        started_at: float,
    ) -> EmbeddingResponse:
        inputs = payload.input if isinstance(payload.input, list) else [payload.input]
        prompt_tokens = sum(estimate_tokens(text) for text in inputs)
        decision = self._route(
            requested_model=payload.model,
            strategy=RoutingStrategy.balanced,
            capability="embeddings",
            estimated_prompt_tokens=prompt_tokens,
        )
        cache_key = stable_cache_key(
            "embeddings",
            {
                "model": decision.model.model_id,
                "version": decision.model.model_version,
                "input": inputs,
            },
        )
        cached = await self._cache.get(cache_key)
        if cached:
            CACHE_HITS.labels(endpoint="/v1/embeddings").inc()
            body = json.loads(cached)
            body["request_id"] = request_id
            body["latency_ms"] = _latency_ms(started_at)
            body["cached"] = True
            return EmbeddingResponse(**body)
        CACHE_MISSES.labels(endpoint="/v1/embeddings").inc()

        provider = self._provider_factory.get_provider(decision.model.provider)
        async with self._semaphore:
            started = perf_counter()
            result = await provider.embeddings(decision.model.model_id, inputs)
            INFERENCE_LATENCY.labels(
                model=decision.model.model_id,
                provider=decision.model.provider,
            ).observe(perf_counter() - started)
        usage = build_usage(result.prompt_tokens, 0, estimated=result.token_counts_estimated)
        response = EmbeddingResponse(
            request_id=request_id,
            model_requested=payload.model,
            model_used=decision.model.model_id,
            model_version=decision.model.model_version,
            embeddings=result.embeddings,
            latency_ms=_latency_ms(started_at),
            cached=False,
            usage=usage,
        )
        await self._cache.set(
            cache_key,
            response.model_dump_json(),
            self._settings.cache_ttl_seconds,
        )
        return response

    async def rag_query(
        self,
        request_id: str,
        payload: RagQueryRequest,
        started_at: float,
    ) -> RagResponse:
        if self._rag_pipeline is None:
            base = await self._generate_response(
                request_id=request_id,
                started_at=started_at,
                model=payload.model,
                prompt=payload.query,
                temperature=payload.temperature,
                max_tokens=payload.max_tokens,
                top_p=payload.top_p,
                routing_strategy=payload.routing_strategy,
                use_rag=False,
                metadata={"rag_disabled_reason": "pipeline_not_configured", **payload.metadata},
            )
            return RagResponse(**base.model_dump(), sources=[])

        results = await self._rag_pipeline.retrieve(
            query=payload.query,
            collection=payload.collection,
            top_k=payload.top_k,
            similarity_threshold=payload.similarity_threshold,
            metadata_filter=payload.metadata_filter,
        )
        prompt = self._rag_pipeline.augment_prompt(payload.query, results)
        base = await self._generate_response(
            request_id=request_id,
            started_at=started_at,
            model=payload.model,
            prompt=prompt,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            top_p=payload.top_p,
            routing_strategy=payload.routing_strategy,
            use_rag=True,
            metadata={"collection": payload.collection, **payload.metadata},
            cache_context=[result.document.chunk_id for result in results],
        )
        return RagResponse(
            **base.model_dump(),
            sources=[
                RagSource(
                    document_id=result.document.document_id,
                    chunk_id=result.document.chunk_id,
                    score=result.score,
                    text=result.document.text,
                    metadata=result.document.metadata,
                )
                for result in results
            ],
        )

    async def _generate_response(
        self,
        *,
        request_id: str,
        started_at: float,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        routing_strategy: RoutingStrategy,
        use_rag: bool,
        metadata: dict[str, Any],
        cache_context: list[str] | None = None,
    ) -> GatewayResponse:
        self._policy_engine.validate_prompt(prompt)
        prompt_tokens = estimate_tokens(prompt)
        decision = self._route(
            requested_model=model,
            strategy=routing_strategy,
            capability="text-generation",
            estimated_prompt_tokens=prompt_tokens,
        )
        cache_key = stable_cache_key(
            "generate",
            {
                "model": decision.model.model_id,
                "version": decision.model.model_version,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "rag_context": cache_context or [],
            },
        )
        cached = await self._cache.get(cache_key)
        if cached:
            CACHE_HITS.labels(endpoint="/v1/generate").inc()
            body = json.loads(cached)
            body["request_id"] = request_id
            body["latency_ms"] = _latency_ms(started_at)
            body["cached"] = True
            return GatewayResponse(**body)
        CACHE_MISSES.labels(endpoint="/v1/generate").inc()

        result_model = decision.model
        provider_result = None
        fallback_attempts = []
        for candidate_id in self._router.fallback_chain(decision.model.model_id):
            candidate_model = result_model if candidate_id == result_model.model_id else None
            if candidate_model is None:
                # Full fallback registry expansion is added when remote providers are configured.
                continue
            circuit = self._circuits.setdefault(candidate_model.model_id, CircuitBreaker())
            if not circuit.allow_request():
                fallback_attempts.append(
                    {"model": candidate_model.model_id, "state": circuit.state},
                )
                continue
            provider = self._provider_factory.get_provider(candidate_model.provider)
            try:
                async with self._semaphore:
                    started = perf_counter()
                    selected_provider = provider
                    selected_model = candidate_model

                    async def invoke_provider(
                        selected_provider=selected_provider,
                        selected_model=selected_model,
                    ):
                        return await selected_provider.generate(
                            selected_model.model_id,
                            prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                        )

                    provider_result = await retry_async(
                        invoke_provider,
                        attempts=2,
                    )
                    INFERENCE_LATENCY.labels(
                        model=candidate_model.model_id,
                        provider=candidate_model.provider,
                    ).observe(perf_counter() - started)
                circuit.record_success()
                result_model = candidate_model
                break
            except Exception as exc:
                circuit.record_failure()
                fallback_attempts.append(
                    {"model": candidate_model.model_id, "error": exc.__class__.__name__},
                )
                FALLBACK_TOTAL.labels(model=candidate_model.model_id).inc()

        if provider_result is None:
            raise ModelUnavailableError("All eligible provider attempts failed")

        self._policy_engine.validate_response(provider_result.text)
        usage = build_usage(
            provider_result.prompt_tokens,
            provider_result.completion_tokens,
            estimated=provider_result.token_counts_estimated,
        )
        TOKENS_GENERATED.labels(model=result_model.model_id).inc(usage.completion_tokens)
        MODEL_REQUESTS.labels(
            model=result_model.model_id,
            provider=result_model.provider,
            status="success",
        ).inc()
        response = GatewayResponse(
            request_id=request_id,
            model_requested=model,
            model_used=result_model.model_id,
            model_version=result_model.model_version,
            routing_strategy=routing_strategy,
            response=provider_result.text,
            latency_ms=_latency_ms(started_at),
            cached=False,
            usage=usage,
            estimated_cost=estimate_cost(result_model, usage),
            metadata={
                **metadata,
                "use_rag": use_rag,
                "routing_score": decision.score,
                "candidates_considered": decision.candidates_considered,
                "fallback_attempts": fallback_attempts,
                **provider_result.metadata,
            },
        )
        await self._cache.set(
            cache_key,
            response.model_dump_json(),
            self._settings.cache_ttl_seconds,
        )
        self.lineage_records.append(
            LineageRecord(
                request_id=request_id,
                routing_strategy=str(routing_strategy),
                model_id=result_model.model_id,
                model_version=result_model.model_version,
                retrieval_context_ids=cache_context or [],
                cached=False,
                metadata={"estimated_cost": response.estimated_cost},
            )
        )
        return response

    def _route(
        self,
        *,
        requested_model: str,
        strategy: RoutingStrategy,
        capability: str,
        estimated_prompt_tokens: int,
    ) -> RoutingDecision:
        decision = self._router.route(
            requested_model=requested_model,
            strategy=strategy,
            capability=capability,
            estimated_prompt_tokens=estimated_prompt_tokens,
            resource_snapshot=self._resource_monitor.snapshot(),
        )
        ROUTING_DECISIONS.labels(
            model=decision.model.model_id,
            routing_strategy=str(strategy),
        ).inc()
        return decision


def _messages_to_prompt(messages: list[Any]) -> str:
    return "\n".join(f"{message.role}: {message.content}" for message in messages)


def _latency_ms(started_at: float) -> float:
    return round((perf_counter() - started_at) * 1000, 3)
