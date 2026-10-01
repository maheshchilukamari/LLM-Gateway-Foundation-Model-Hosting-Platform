"""Public LLM gateway endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.api.dependencies import engine_dependency
from app.core.rate_limit import enforce_rate_limit
from app.core.security import require_api_key
from app.inference.engine import InferenceEngine
from app.schemas.requests import (
    ChatCompletionRequest,
    EmbeddingRequest,
    GenerateRequest,
    RagQueryRequest,
)
from app.schemas.responses import EmbeddingResponse, GatewayResponse, RagResponse

router = APIRouter(
    prefix="/v1",
    tags=["gateway"],
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)
EngineDep = Annotated[InferenceEngine, Depends(engine_dependency)]


@router.post("/chat/completions", response_model=GatewayResponse)
async def chat_completions(
    request: Request,
    payload: ChatCompletionRequest,
    engine: EngineDep,
) -> JSONResponse:
    response = await engine.chat(request.state.request_id, payload, request.state.started_at)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json"),
    )


@router.post("/generate", response_model=GatewayResponse)
async def generate(
    request: Request,
    payload: GenerateRequest,
    engine: EngineDep,
) -> JSONResponse:
    response = await engine.generate(request.state.request_id, payload, request.state.started_at)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json"),
    )


@router.post("/embeddings", response_model=EmbeddingResponse)
async def embeddings(
    request: Request,
    payload: EmbeddingRequest,
    engine: EngineDep,
) -> JSONResponse:
    response = await engine.embeddings(request.state.request_id, payload, request.state.started_at)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json"),
    )


@router.post("/rag/query", response_model=RagResponse)
async def rag_query(
    request: Request,
    payload: RagQueryRequest,
    engine: EngineDep,
) -> JSONResponse:
    response = await engine.rag_query(request.state.request_id, payload, request.state.started_at)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json"),
    )
