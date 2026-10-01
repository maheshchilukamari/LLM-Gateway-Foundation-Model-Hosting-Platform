"""Model discovery endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import registry_dependency
from app.gateway.registry import ModelRegistry
from app.schemas.models import ModelListResponse, ModelMetadata

router = APIRouter(prefix="/v1/models", tags=["models"])
RegistryDep = Annotated[ModelRegistry, Depends(registry_dependency)]


@router.get("", response_model=ModelListResponse)
async def list_models(registry: RegistryDep) -> ModelListResponse:
    return ModelListResponse(models=registry.list_models())


@router.get("/{model_id:path}", response_model=ModelMetadata)
async def get_model(
    model_id: str,
    registry: RegistryDep,
) -> ModelMetadata:
    model = registry.get_model(model_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model not found: {model_id}",
        )
    return model
