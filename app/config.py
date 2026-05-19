from pathlib import Path
import os

DATA_DIR = Path("data")
DOCUMENTS_PATH = DATA_DIR / "documents.json"
CHUNKS_PATH = DATA_DIR / "chunks.json"
EMBEDDING_CACHE_PATH = DATA_DIR / "embedding_cache.json"

DEFAULT_TOP_K = 5
MIN_SCORE_THRESHOLD = 0.12
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "mock")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", OPENAI_BASE_URL)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_LLM_MODEL = os.getenv("DEEPSEEK_LLM_MODEL", "deepseek-v4-flash")
