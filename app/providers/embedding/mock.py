import hashlib
import math

from app.providers.embedding.base import BaseEmbeddingProvider


class MockEmbeddingProvider(BaseEmbeddingProvider):
    model_name = "mock-embedding-v1"

    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * 256
        for token in self._tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = digest[0] % len(vector)
            vector[idx] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def _tokens(self, text: str) -> list[str]:
        normalized = "".join(text.lower().split())
        tokens = [item for item in text.lower().split() if item]
        tokens.extend(normalized[index : index + 2] for index in range(max(len(normalized) - 1, 0)))
        tokens.extend(normalized[index : index + 3] for index in range(max(len(normalized) - 2, 0)))
        return tokens
