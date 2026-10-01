from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())
headers = {"X-API-Key": "dev-api-key"}


def test_root_endpoint_returns_api_discovery() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "LLM Gateway" in response.text
    assert "/docs" in response.text


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_endpoint() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_list_models() -> None:
    response = client.get("/v1/models")

    assert response.status_code == 200
    assert len(response.json()["models"]) >= 3


def test_chat_completion_contract() -> None:
    response = client.post(
        "/v1/chat/completions",
        headers=headers,
        json={
            "model": "auto",
            "messages": [{"role": "user", "content": "Explain vector databases."}],
            "temperature": 0.7,
            "max_tokens": 300,
            "routing_strategy": "balanced",
            "use_rag": False,
            "metadata": {"application": "demo"},
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["model_requested"] == "auto"
    assert body["routing_strategy"] == "balanced"
    assert body["model_used"] != "pending-provider-phase"
    assert body["usage"]["total_tokens"] > 0
    assert body["request_id"]
    assert response.headers["x-request-id"] == body["request_id"]


def test_generate_cache_hit_contract() -> None:
    payload = {"model": "auto", "prompt": "Explain why caching helps LLM gateways."}

    first = client.post("/v1/generate", headers=headers, json=payload)
    second = client.post("/v1/generate", headers=headers, json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert first.json()["request_id"] != second.json()["request_id"]


def test_embeddings_contract() -> None:
    response = client.post(
        "/v1/embeddings",
        headers=headers,
        json={"model": "auto", "input": "vector databases store embeddings"},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["embeddings"]
    assert body["usage"]["prompt_tokens"] > 0


def test_rag_query_returns_sources() -> None:
    response = client.post(
        "/v1/rag/query",
        headers=headers,
        json={
            "model": "auto",
            "query": "How do vector databases help RAG?",
            "top_k": 2,
            "similarity_threshold": 0.0,
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["sources"]
    assert body["metadata"]["collection"] == "default"


def test_gateway_requires_api_key() -> None:
    response = client.post(
        "/v1/generate",
        json={"prompt": "hello"},
    )

    assert response.status_code == 401


def test_admin_requires_admin_key() -> None:
    response = client.get("/v1/admin/stats", headers=headers)

    assert response.status_code == 403
