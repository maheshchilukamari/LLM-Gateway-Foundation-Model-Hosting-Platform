"""Request lineage records."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class LineageRecord(BaseModel):
    request_id: str
    routing_strategy: str
    model_id: str
    model_version: str
    retrieval_context_ids: list[str] = Field(default_factory=list)
    cached: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

