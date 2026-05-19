from app import config
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.embedding.mock import MockEmbeddingProvider
from app.providers.embedding.openai_provider import OpenAIEmbeddingProvider
from app.providers.llm.base import BaseLLMProvider
from app.providers.llm.deepseek_provider import DeepSeekLLMProvider
from app.providers.llm.mock import MockLLMProvider
from app.providers.llm.openai_provider import OpenAILLMProvider


def create_embedding_provider() -> BaseEmbeddingProvider:
    provider = config.EMBEDDING_PROVIDER.lower()
    if provider == "mock":
        return MockEmbeddingProvider()
    if provider == "openai":
        return OpenAIEmbeddingProvider(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=config.OPENAI_EMBEDDING_MODEL,
        )
    if provider == "openai-compatible":
        return OpenAIEmbeddingProvider(
            api_key=config.EMBEDDING_API_KEY,
            base_url=config.EMBEDDING_BASE_URL,
            model=config.EMBEDDING_MODEL,
        )
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {config.EMBEDDING_PROVIDER}")


def create_llm_provider() -> BaseLLMProvider:
    provider = config.LLM_PROVIDER.lower()
    if provider == "mock":
        return MockLLMProvider()
    if provider == "openai":
        return OpenAILLMProvider(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=config.OPENAI_LLM_MODEL,
        )
    if provider == "deepseek":
        return DeepSeekLLMProvider(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
            model=config.DEEPSEEK_LLM_MODEL,
        )
    raise ValueError(f"Unsupported LLM_PROVIDER: {config.LLM_PROVIDER}")
