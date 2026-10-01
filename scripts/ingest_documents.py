"""Ingest sample documents through the in-process RAG pipeline."""

import asyncio

from app.api.dependencies import get_engine


async def main() -> None:
    engine = get_engine()
    if engine._rag_pipeline is None:  # noqa: SLF001
        print("RAG pipeline is not configured")
        return
    count = await engine._rag_pipeline.ingest_text(  # noqa: SLF001
        document_id="sample-platform-overview",
        collection="default",
        text=(
            "The LLM Gateway routes requests across models, applies governance "
            "policies, records lineage, and exposes metrics for platform operators."
        ),
        metadata={"source": "scripts/ingest_documents.py"},
    )
    print(f"Ingested {count} chunks into collection 'default'")


if __name__ == "__main__":
    asyncio.run(main())

