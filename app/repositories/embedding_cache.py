from app.repositories.json_store import JsonStore


class EmbeddingCache:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def _key(self, content_hash: str, embedding_model: str) -> str:
        return f"{embedding_model}:{content_hash}"

    def get(self, content_hash: str, embedding_model: str) -> list[float] | None:
        cache = self.store.load_embedding_cache()
        return cache.get(self._key(content_hash, embedding_model))

    def set(self, content_hash: str, embedding_model: str, embedding: list[float]) -> None:
        cache = self.store.load_embedding_cache()
        cache[self._key(content_hash, embedding_model)] = embedding
        self.store.save_embedding_cache(cache)
