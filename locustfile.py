"""Locust load tests for gateway scenarios."""

from locust import HttpUser, between, task


class GatewayUser(HttpUser):
    wait_time = between(0.2, 1.0)

    @task(4)
    def generate_auto(self) -> None:
        self.client.post(
            "/v1/generate",
            headers={"X-API-Key": "dev-api-key"},
            json={
                "model": "auto",
                "prompt": "Explain vector databases.",
                "routing_strategy": "balanced",
            },
        )

    @task(2)
    def cache_hit_candidate(self) -> None:
        self.client.post(
            "/v1/generate",
            headers={"X-API-Key": "dev-api-key"},
            json={
                "model": "auto",
                "prompt": "What is an LLM gateway?",
                "routing_strategy": "lowest_cost",
            },
        )

    @task(1)
    def rag_query(self) -> None:
        self.client.post(
            "/v1/rag/query",
            headers={"X-API-Key": "dev-api-key"},
            json={"query": "How does RAG use vector databases?", "model": "auto", "top_k": 2},
        )
