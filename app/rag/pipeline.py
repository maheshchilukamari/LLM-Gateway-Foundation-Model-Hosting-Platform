"""Retrieval-augmented generation pipeline."""

from app.providers.base import ModelProvider
from app.rag.chunker import chunk_text
from app.rag.retriever import Retriever
from app.rag.vector_store import InMemoryVectorStore, SearchResult, VectorDocument


class RagPipeline:
    """Local RAG pipeline with in-memory vector storage."""

    def __init__(
        self,
        *,
        embedding_provider: ModelProvider,
        embedding_model_id: str,
        vector_store: InMemoryVectorStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._embedding_model_id = embedding_model_id
        self._vector_store = vector_store
        self._retriever = Retriever(vector_store)

    async def ingest_text(
        self,
        *,
        document_id: str,
        text: str,
        collection: str = "default",
        metadata: dict[str, object] | None = None,
    ) -> int:
        chunks = chunk_text(text)
        if not chunks:
            return 0
        embeddings = (
            await self._embedding_provider.embeddings(self._embedding_model_id, chunks)
        ).embeddings
        documents = [
            VectorDocument(
                document_id=document_id,
                chunk_id=f"{document_id}:{index}",
                text=chunk,
                embedding=embeddings[index],
                metadata=dict(metadata or {}),
            )
            for index, chunk in enumerate(chunks)
        ]
        self._vector_store.add(collection, documents)
        return len(documents)

    async def retrieve(
        self,
        *,
        query: str,
        collection: str,
        top_k: int,
        similarity_threshold: float,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[SearchResult]:
        query_embedding = (
            await self._embedding_provider.embeddings(self._embedding_model_id, [query])
        ).embeddings[0]
        return self._retriever.retrieve(
            collection=collection,
            query_embedding=query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metadata_filter=metadata_filter,
        )

    @staticmethod
    def augment_prompt(query: str, results: list[SearchResult]) -> str:
        if not results:
            return query
        context = "\n\n".join(
            f"Source {index + 1} ({result.document.chunk_id}): {result.document.text}"
            for index, result in enumerate(results)
        )
        return (
            "Use the retrieved context to answer. If the context is insufficient, "
            "say what is missing.\n\n"
            f"Context:\n{context}\n\nQuestion:\n{query}"
        )

