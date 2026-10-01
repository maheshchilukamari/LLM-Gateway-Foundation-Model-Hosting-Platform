"""Gateway response schemas."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated: bool = True


class GatewayResponse(BaseModel):
    request_id: str
    model_requested: str
    model_used: str
    model_version: str
    routing_strategy: str
    response: str
    latency_ms: float
    cached: bool
    usage: TokenUsage
    estimated_cost: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    request_id: str
    model_requested: str
    model_used: str
    model_version: str
    embeddings: list[list[float]]
    latency_ms: float
    cached: bool
    usage: TokenUsage
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RagSource(BaseModel):
    document_id: str
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagResponse(GatewayResponse):
    sources: list[RagSource] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    version: str


class DependencyStatus(BaseModel):
    name: str
    status: str
    required: bool = True
    detail: str | None = None


class ReadyResponse(BaseModel):
    status: str
    dependencies: list[DependencyStatus]


class ErrorResponse(BaseModel):
    request_id: str | None = None
    error: str
    detail: str
