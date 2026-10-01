"""Seed database metadata from YAML model configuration."""

import asyncio

from app.core.config import get_settings
from app.db.models import Base, ModelRecord
from app.db.session import AsyncSessionLocal, engine
from app.gateway.registry import ModelRegistry


async def main() -> None:
    settings = get_settings()
    registry = ModelRegistry(settings)
    registry.load()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        for model in registry.list_models():
            session.add(
                ModelRecord(
                    model_id=model.model_id,
                    provider=model.provider,
                    task_type=model.task_type,
                    metadata_json=model.model_dump(mode="json"),
                )
            )
        await session.commit()
    print(f"Seeded {len(registry.list_models())} model records")


if __name__ == "__main__":
    asyncio.run(main())

