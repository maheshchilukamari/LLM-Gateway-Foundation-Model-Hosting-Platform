"""Retriever abstraction."""

from app.rag.vector_store import InMemoryVectorStore, SearchResult


class Retriever:
    """Retrieve relevant context chunks from a vector store."""

    def __init__(self, vector_store: InMemoryVectorStore) -> None:
        self._vector_store = vector_store

    def retrieve(
        self,
        *,
        collection: str,
        query_embedding: list[float],
        top_k: int,
        similarity_threshold: float,
        metadata_filter: dict[str, object] | None,
    ) -> list[SearchResult]:
        return self._vector_store.search(
            collection,
            query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metadata_filter=metadata_filter,
        )

