import math
import re

from app.core.schemas import Chunk, SearchResult
from app.repositories.json_store import JsonStore
from app.vectorstores.base import BaseVectorStore


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def text_tokens(text: str) -> set[str]:
    normalized = "".join(text.lower().split())
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    grams = {
        normalized[index : index + size]
        for size in (2, 3, 4)
        for index in range(max(len(normalized) - size + 1, 0))
    }
    return {token for token in words | grams if token}


def keyword_overlap(query: str, content: str) -> float:
    query_tokens = text_tokens(query)
    if not query_tokens:
        return 0.0
    content_tokens = text_tokens(content)
    matched = query_tokens & content_tokens
    return len(matched) / len(query_tokens)


class JsonVectorStore(BaseVectorStore):
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def add_chunks(self, chunks: list[Chunk]) -> None:
        existing = self.store.load_chunks()
        existing.extend(chunks)
        self.store.save_chunks(existing)

    def search(
        self,
        query_vector: list[float],
        top_k: int,
        document_ids: list[str] | None = None,
        active_versions: dict[str, int] | None = None,
        query_text: str | None = None,
    ) -> list[SearchResult]:
        candidates = self.store.load_chunks()

        if document_ids:
            allowed = set(document_ids)
            candidates = [chunk for chunk in candidates if chunk.document_id in allowed]

        if active_versions:
            candidates = [
                chunk
                for chunk in candidates
                if active_versions.get(chunk.document_id) == chunk.document_version
            ]

        scored = []
        for chunk in candidates:
            vector_score = cosine_similarity(query_vector, chunk.embedding)
            text_score = keyword_overlap(query_text or "", chunk.content)
            score = max(vector_score, text_score)
            scored.append(SearchResult(chunk=chunk, score=score))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

    def delete_by_document(self, document_id: str, version: int | None = None) -> int:
        chunks = self.store.load_chunks()
        kept = []
        removed = 0
        for chunk in chunks:
            matches = chunk.document_id == document_id and (
                version is None or chunk.document_version == version
            )
            if matches:
                removed += 1
            else:
                kept.append(chunk)
        self.store.save_chunks(kept)
        return removed

    def count_by_document(self, document_id: str, version: int | None = None) -> int:
        return sum(
            1
            for chunk in self.store.load_chunks()
            if chunk.document_id == document_id
            and (version is None or chunk.document_version == version)
        )
