import json
from pathlib import Path
from typing import Any

from app.config import CHUNKS_PATH, DOCUMENTS_PATH, EMBEDDING_CACHE_PATH
from app.core.schemas import Chunk, Document


class JsonStore:
    def __init__(
        self,
        documents_path: Path = DOCUMENTS_PATH,
        chunks_path: Path = CHUNKS_PATH,
        embedding_cache_path: Path = EMBEDDING_CACHE_PATH,
    ) -> None:
        self.documents_path = documents_path
        self.chunks_path = chunks_path
        self.embedding_cache_path = embedding_cache_path
        self.documents_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def load_documents(self) -> list[Document]:
        return [Document.model_validate(item) for item in self._load_json(self.documents_path, [])]

    def save_documents(self, documents: list[Document]) -> None:
        self._save_json(self.documents_path, [item.model_dump(mode="json") for item in documents])

    def load_chunks(self) -> list[Chunk]:
        return [Chunk.model_validate(item) for item in self._load_json(self.chunks_path, [])]

    def save_chunks(self, chunks: list[Chunk]) -> None:
        self._save_json(self.chunks_path, [item.model_dump(mode="json") for item in chunks])

    def load_embedding_cache(self) -> dict[str, list[float]]:
        return self._load_json(self.embedding_cache_path, {})

    def save_embedding_cache(self, cache: dict[str, list[float]]) -> None:
        self._save_json(self.embedding_cache_path, cache)
