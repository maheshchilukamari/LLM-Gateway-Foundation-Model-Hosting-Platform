"""Small smoke benchmark for local development.

For real load tests, use `locustfile.py` and save measured outputs under
benchmarks/. Do not convert this smoke test into resume metrics.
"""

import asyncio
from statistics import mean
from time import perf_counter

import httpx


async def main() -> None:
    latencies: list[float] = []
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=30) as client:
        for _ in range(5):
            started = perf_counter()
            response = await client.post(
                "/v1/generate",
                headers={"X-API-Key": "dev-api-key"},
                json={"prompt": "Explain why LLM gateways are useful.", "model": "auto"},
            )
            response.raise_for_status()
            latencies.append((perf_counter() - started) * 1000)
    print(f"Completed {len(latencies)} requests; average latency: {mean(latencies):.2f} ms")


if __name__ == "__main__":
    asyncio.run(main())

