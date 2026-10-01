"""Protected administration endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import registry_dependency
from app.core.security import require_admin_api_key
from app.gateway.registry import ModelRegistry
from app.schemas.models import ModelAvailability

router = APIRouter(
    prefix="/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_api_key)],
)
RegistryDep = Annotated[ModelRegistry, Depends(registry_dependency)]


@router.get("/models")
async def admin_models(registry: RegistryDep) -> dict[str, object]:
    return {"models": [model.model_dump() for model in registry.list_models()]}


@router.get("/models/health")
async def admin_model_health(
    registry: RegistryDep,
) -> dict[str, object]:
    return {
        "models": [
            {
                "model_id": model.model_id,
                "provider": model.provider,
                "health_status": model.health_status,
                "availability": model.availability,
            }
            for model in registry.list_models()
        ]
    }


@router.get("/stats")
async def admin_stats(registry: RegistryDep) -> dict[str, object]:
    return {
        "registered_models": len(registry.list_models()),
        "healthy_model_available": registry.has_healthy_model(),
        "phase": "phase_1_foundation",
    }


@router.post("/models/{model_id:path}/enable")
async def enable_model(model_id: str, registry: RegistryDep) -> dict[str, object]:
    model = registry.set_availability(model_id, ModelAvailability.enabled)
    if model is None:
        return {"updated": False, "model_id": model_id, "reason": "not_found"}
    return {"updated": True, "model": model.model_dump()}


@router.post("/models/{model_id:path}/disable")
async def disable_model(model_id: str, registry: RegistryDep) -> dict[str, object]:
    model = registry.set_availability(model_id, ModelAvailability.disabled)
    if model is None:
        return {"updated": False, "model_id": model_id, "reason": "not_found"}
    return {"updated": True, "model": model.model_dump()}
