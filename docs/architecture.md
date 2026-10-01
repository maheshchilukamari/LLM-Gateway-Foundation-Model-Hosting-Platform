# Architecture

## Objective

I implemented a centralized LLM Gateway that gives applications one stable API for multiple model providers, retrieval pipelines, policy checks, caching, observability, and governance controls.

The local version is intentionally runnable on a normal development laptop. Production-oriented extension points are included for Redis, PostgreSQL, Kubernetes, AWS, OpenTelemetry, and external model providers.

## High-Level Components

```mermaid
flowchart TD
    Client[Client Application] --> Gateway[FastAPI API Gateway]
    Gateway --> Auth[Authentication and Request Validation]
    Auth --> Policy[Policy Engine]
    Policy --> CacheLookup[Cache Lookup]
    CacheLookup --> Router[Dynamic Model Router]
    Router --> Rag{Use RAG?}
    Rag -->|Yes| Retriever[RAG Retriever and Prompt Builder]
    Rag -->|No| Provider[Model Provider Interface]
    Retriever --> Provider
    Provider --> Validator[Response Validation]
    Validator --> CacheWrite[Cache Write]
    CacheWrite --> Obs[Metrics, Logs, Traces, Lineage]
    Obs --> Response[Standardized Response]
```

## Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant A as FastAPI Gateway
    participant P as Policy Engine
    participant R as Router
    participant V as Vector Store
    participant M as Model Provider
    participant O as Observability

    C->>A: POST /v1/chat/completions
    A->>A: Request ID, auth, schema validation
    A->>P: Enforce request policies
    A->>R: Select model using routing strategy
    alt RAG enabled
        A->>V: Retrieve top-k context chunks
    end
    A->>M: Invoke selected model
    M-->>A: Raw provider response
    A->>A: Validate, normalize, estimate tokens/cost
    A->>O: Metrics, structured logs, traces, lineage
    A-->>C: Standardized gateway response
```

## Repository Structure

```text
llm-gateway-platform/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── dependencies.py
│   │   └── middleware/
│   ├── cache/
│   ├── core/
│   ├── db/
│   ├── gateway/
│   ├── governance/
│   ├── inference/
│   ├── observability/
│   ├── providers/
│   ├── rag/
│   ├── schemas/
│   └── main.py
├── configs/
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/
├── sample_data/
├── benchmarks/
├── monitoring/
├── infra/
│   ├── kubernetes/
│   ├── helm/
│   └── terraform/
├── docs/
├── .github/workflows/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Implementation Phases

1. Project foundation, FastAPI, configuration, schemas, health endpoints.
2. Model provider abstraction and Hugging Face inference.
3. Model registry.
4. Dynamic routing engine.
5. Caching and token accounting.
6. Reliability, retry, fallback, circuit breaker.
7. RAG.
8. Observability.
9. Security and rate limiting.
10. Database, versioning, lineage, governance.
11. Docker and Docker Compose.
12. Kubernetes and Helm.
13. AWS and Terraform architecture.
14. Testing and load testing.
15. GitHub Actions.
16. Documentation, README, diagrams, and university presentation guide.

## Initial Python Dependencies

- `fastapi` and `uvicorn` for the HTTP gateway.
- `pydantic` and `pydantic-settings` for request contracts and configuration.
- `PyYAML` for model, routing, and policy configuration.
- `structlog` for JSON logging.
- `prometheus-client` for metrics.
- `pytest`, `httpx`, and `ruff` for tests and quality checks.

Later phases add `torch`, `transformers`, `sentence-transformers`, `redis`, `SQLAlchemy`, `Alembic`, `psutil`, vector store dependencies, OpenTelemetry packages, and Locust.

## Local Models

The local development profile starts with lightweight Hugging Face models:

- `distilgpt2`: small causal text-generation model for local generation paths.
- `google/flan-t5-small`: instruction-following text2text model that can support RAG prompts better than a plain causal model.
- `sentence-transformers/all-MiniLM-L6-v2`: compact embedding model for semantic search and RAG.

These are intentionally CPU-friendly compared with larger foundation models. GPU support will be automatic when available, but not required.

## Real vs Abstracted in Local Development

Real local implementation:

- FastAPI API contracts.
- API-key authentication.
- YAML model metadata.
- Dynamic routing logic.
- Hugging Face local model execution.
- Redis-backed caching with in-memory fallback.
- Local vector search for RAG.
- Prometheus metrics.
- Structured logging.
- Docker Compose.
- Tests.

Production-style abstraction or documented extension:

- External hosted model providers.
- Multi-node distributed inference.
- GPU node pool orchestration.
- Enterprise-grade policy workflows.
- Full AWS environment provisioning.
- Human review systems.
- Advanced queueing and batch schedulers.

The project should not claim production benchmark results until load tests are run and saved under `benchmarks/`.

## Laptop Resource Constraints

Local inference can be slow on CPU and may require several gigabytes of disk space for model downloads. The default model set avoids GPU-only dependencies, but first-run Hugging Face downloads can still take time. Larger models, high concurrency, and high `max_tokens` settings should be treated as production or GPU-node scenarios.
