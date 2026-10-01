"""Local in-memory vector store for RAG demos."""

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VectorDocument:
    document_id: str
    chunk_id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    document: VectorDocument
    score: float


class InMemoryVectorStore:
    """Simple cosine-similarity vector store."""

    def __init__(self) -> None:
        self._collections: dict[str, list[VectorDocument]] = {}

    def add(self, collection: str, documents: list[VectorDocument]) -> None:
        self._collections.setdefault(collection, []).extend(documents)

    def search(
        self,
        collection: str,
        query_embedding: list[float],
        *,
        top_k: int,
        similarity_threshold: float,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        documents = self._collections.get(collection, [])
        results: list[SearchResult] = []
        for document in documents:
            if metadata_filter and not _metadata_matches(document.metadata, metadata_filter):
                continue
            score = _cosine_similarity(query_embedding, document.embedding)
            if score >= similarity_threshold:
                results.append(SearchResult(document=document, score=round(score, 6)))
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]

    def count(self, collection: str = "default") -> int:
        return len(self._collections.get(collection, []))


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(value * value for value in left)) or 1.0
    right_norm = math.sqrt(sum(value * value for value in right)) or 1.0
    return numerator / (left_norm * right_norm)


def _metadata_matches(metadata: dict[str, Any], metadata_filter: dict[str, Any]) -> bool:
    return all(metadata.get(key) == value for key, value in metadata_filter.items())

