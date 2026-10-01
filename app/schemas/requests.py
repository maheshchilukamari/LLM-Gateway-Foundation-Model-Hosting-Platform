"""Gateway request schemas."""

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoutingStrategy(StrEnum):
    lowest_latency = "lowest_latency"
    lowest_cost = "lowest_cost"
    highest_quality = "highest_quality"
    highest_throughput = "highest_throughput"
    balanced = "balanced"
    resource_aware = "resource_aware"
    fallback = "fallback"


class RequestPriority(StrEnum):
    low = "low"
    normal = "normal"
    high = "high"


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=20_000)


class GatewayRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(default="auto", min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1, le=4096)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    routing_strategy: RoutingStrategy = RoutingStrategy.balanced
    use_rag: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    priority: RequestPriority = RequestPriority.normal
    stream: bool = False

    @field_validator("metadata")
    @classmethod
    def metadata_is_small(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(value) > 50:
            raise ValueError("metadata may contain at most 50 keys")
        return value


class ChatCompletionRequest(GatewayRequestBase):
    messages: list[ChatMessage] = Field(min_length=1, max_length=64)


class GenerateRequest(GatewayRequestBase):
    prompt: str = Field(min_length=1, max_length=20_000)


class EmbeddingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(default="auto", min_length=1)
    input: str | list[str] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagQueryRequest(GatewayRequestBase):
    query: str = Field(min_length=1, max_length=20_000)
    collection: str = "default"
    top_k: int = Field(default=4, ge=1, le=20)
    similarity_threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    metadata_filter: dict[str, Any] | None = None
    use_rag: bool = True

