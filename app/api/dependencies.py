"""FastAPI dependency helpers."""

from functools import lru_cache

from app.cache.memory_cache import MemoryCache
from app.core.config import get_settings
from app.gateway.registry import ModelRegistry
from app.gateway.router import ModelRouter
from app.governance.policies import PolicyEngine
from app.inference.engine import InferenceEngine
from app.inference.resource_monitor import ResourceMonitor
from app.providers.factory import ProviderFactory
from app.rag.pipeline import RagPipeline
from app.rag.vector_store import InMemoryVectorStore


@lru_cache
def get_registry() -> ModelRegistry:
    settings = get_settings()
    registry = ModelRegistry(settings)
    registry.load()
    return registry


async def registry_dependency() -> ModelRegistry:
    return get_registry()


@lru_cache
def get_engine() -> InferenceEngine:
    settings = get_settings()
    registry = get_registry()
    provider_factory = ProviderFactory(prefer_mock=settings.prefer_mock_provider)
    vector_store = InMemoryVectorStore()
    embedding_provider = provider_factory.get_provider("mock")
    rag_pipeline = RagPipeline(
        embedding_provider=embedding_provider,
        embedding_model_id=settings.embedding_model_id,
        vector_store=vector_store,
    )
    engine = InferenceEngine(
        settings=settings,
        router=ModelRouter(settings, registry),
        provider_factory=provider_factory,
        cache=MemoryCache(),
        policy_engine=PolicyEngine(settings),
        resource_monitor=ResourceMonitor(),
        rag_pipeline=rag_pipeline,
    )
    return engine


async def engine_dependency() -> InferenceEngine:
    engine = get_engine()
    await _seed_rag_once(engine)
    return engine


_rag_seeded = False


async def _seed_rag_once(engine: InferenceEngine) -> None:
    global _rag_seeded
    if _rag_seeded or engine._rag_pipeline is None:  # noqa: SLF001
        return
    await engine._rag_pipeline.ingest_text(  # noqa: SLF001
        document_id="gateway-architecture",
        collection="default",
        text=(
            "An LLM Gateway centralizes authentication, routing, caching, retries, "
            "fallback, observability, policy enforcement, and model governance so "
            "applications do not call every model provider directly."
        ),
        metadata={"source": "sample_data"},
    )
    await engine._rag_pipeline.ingest_text(  # noqa: SLF001
        document_id="vector-databases",
        collection="default",
        text=(
            "Vector databases store embeddings and support similarity search. They "
            "are commonly used in retrieval augmented generation to find relevant "
            "context before prompting a language model."
        ),
        metadata={"source": "sample_data"},
    )
    _rag_seeded = True
