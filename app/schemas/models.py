"""Model metadata schemas."""

from enum import StrEnum
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ModelHealthStatus(StrEnum):
    healthy = "HEALTHY"
    degraded = "DEGRADED"
    unhealthy = "UNHEALTHY"


class ModelAvailability(StrEnum):
    enabled = "enabled"
    disabled = "disabled"


class ModelMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    model_id: str = Field(validation_alias=AliasChoices("model_id", "id"))
    provider: str
    model_family: str | None = None
    model_version: str = "1.0"
    task_type: str
    context_window: int
    device: str = "cpu"
    average_latency_ms: float = 0.0
    estimated_cost_per_1k_tokens: float = 0.0
    max_batch_size: int = 1
    availability: ModelAvailability = ModelAvailability.enabled
    health_status: ModelHealthStatus = ModelHealthStatus.healthy
    quality_score: float = Field(ge=0.0, le=1.0)
    throughput_score: float = Field(default=0.5, ge=0.0, le=1.0)
    supported_capabilities: list[str] = Field(default_factory=list)
    deployment_target: str = "local"
    governance: dict[str, Any] = Field(default_factory=dict)


class ModelListResponse(BaseModel):
    models: list[ModelMetadata]
