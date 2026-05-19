from app.core.schemas import Chunk, SearchResult


class BaseVectorStore:
    def add_chunks(self, chunks: list[Chunk]) -> None:
        raise NotImplementedError

    def search(
        self,
        query_vector: list[float],
        top_k: int,
        document_ids: list[str] | None = None,
        active_versions: dict[str, int] | None = None,
        query_text: str | None = None,
    ) -> list[SearchResult]:
        raise NotImplementedError

    def delete_by_document(self, document_id: str, version: int | None = None) -> int:
        raise NotImplementedError

    def count_by_document(self, document_id: str, version: int | None = None) -> int:
        raise NotImplementedError
