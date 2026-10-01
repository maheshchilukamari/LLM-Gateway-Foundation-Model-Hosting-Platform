"""Health and readiness endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import registry_dependency
from app.core.config import Settings, get_settings
from app.gateway.registry import ModelRegistry
from app.schemas.responses import DependencyStatus, HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])
SettingsDep = Annotated[Settings, Depends(get_settings)]
RegistryDep = Annotated[ModelRegistry, Depends(registry_dependency)]


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDep) -> HealthResponse:
    """Liveness endpoint: process is up."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
        version=settings.api_version,
    )


@router.get("/ready", response_model=ReadyResponse)
async def ready(
    response: Response,
    settings: SettingsDep,
    registry: RegistryDep,
) -> ReadyResponse:
    """Readiness endpoint: core dependencies are usable."""
    dependencies = [
        DependencyStatus(
            name="model_registry",
            status="ok" if registry.list_models() else "error",
            required=True,
        ),
        DependencyStatus(
            name="healthy_model",
            status="ok" if registry.has_healthy_model() else "error",
            required=True,
        ),
        DependencyStatus(
            name="redis",
            status="not_checked",
            required=settings.redis_required,
            detail="Redis connectivity is implemented in the caching phase.",
        ),
        DependencyStatus(
            name="vector_store",
            status="not_checked",
            required=False,
            detail="Vector store readiness is implemented in the RAG phase.",
        ),
    ]
    ready_status = "ready" if all(
        item.status == "ok" or not item.required for item in dependencies
    ) else "not_ready"
    if ready_status != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(status=ready_status, dependencies=dependencies)
