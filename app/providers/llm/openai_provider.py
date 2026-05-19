from app.providers.llm.base import BaseLLMProvider


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str | None,
        model: str,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install openai to use OpenAI-compatible providers") from exc

        if not self.api_key:
            raise RuntimeError("LLM api key is not configured")

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content or ""
