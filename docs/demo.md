# Demo Scenarios

This file tracks my university demo flow. The local demo uses deterministic local inference by default so it can run on a normal laptop without model downloads.

## Scenario 1: Health

```bash
curl http://localhost:8000/health
```

## Scenario 2: Model Discovery

```bash
curl http://localhost:8000/v1/models
```

## Scenario 3: Chat Contract

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Explain vector databases."}],
    "temperature": 0.7,
    "max_tokens": 300,
    "routing_strategy": "balanced",
    "use_rag": false,
    "metadata": {"application": "demo"}
  }'
```

## Scenario 4: Cache Hit

Run the same `/v1/generate` request twice. The second response should include `"cached": true`.

## Scenario 5: RAG Query

```bash
curl -X POST http://localhost:8000/v1/rag/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{"model":"auto","query":"How do vector databases help RAG?","top_k":2,"similarity_threshold":0.0}'
```

## Scenario 6: Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

## Scenario 7: Load Test

```bash
locust -f locustfile.py --host http://localhost:8000
```

Save actual measured results under `benchmarks/` before using any quantified claims.
