from app.providers.embedding.base import BaseEmbeddingProvider


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(
        self,
        api_key: str | None,
        model: str,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.model_name = model
        self.base_url = base_url

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install openai to use OpenAI-compatible embeddings") from exc

        if not self.api_key:
            raise RuntimeError("Embedding api key is not configured")

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.embeddings.create(model=self.model_name, input=texts)
        return [item.embedding for item in response.data]
