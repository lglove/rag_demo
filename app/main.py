from fastapi import FastAPI

from app.api import ask, ui, upload
from app.providers.factory import create_embedding_provider, create_llm_provider
from app.repositories.document_repo import DocumentRepository
from app.repositories.embedding_cache import EmbeddingCache
from app.repositories.json_store import JsonStore
from app.services.document_service import DocumentService
from app.services.qa_service import QAService
from app.vectorstores.memory_store import JsonVectorStore

store = JsonStore()
document_repo = DocumentRepository(store)
embedding_cache = EmbeddingCache(store)
embedding_provider = create_embedding_provider()
llm_provider = create_llm_provider()
vector_store = JsonVectorStore(store)

document_service = DocumentService(
    document_repo=document_repo,
    embedding_cache=embedding_cache,
    embedding_provider=embedding_provider,
    vector_store=vector_store,
)
qa_service = QAService(
    document_repo=document_repo,
    embedding_provider=embedding_provider,
    llm_provider=llm_provider,
    vector_store=vector_store,
)

app = FastAPI(title="Enterprise Knowledge Base RAG Demo")
app.include_router(ui.router)
app.include_router(upload.router)
app.include_router(ask.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
