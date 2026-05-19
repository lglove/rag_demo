from fastapi import HTTPException

from app.config import DEFAULT_TOP_K, MIN_SCORE_THRESHOLD
from app.core.prompt import build_qa_prompt
from app.core.schemas import AskRequest, AskResponse, Source
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.llm.base import BaseLLMProvider
from app.repositories.document_repo import DocumentRepository
from app.vectorstores.base import BaseVectorStore


class QAService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        embedding_provider: BaseEmbeddingProvider,
        llm_provider: BaseLLMProvider,
        vector_store: BaseVectorStore,
    ) -> None:
        self.document_repo = document_repo
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider
        self.vector_store = vector_store

    def ask(self, request: AskRequest) -> AskResponse:
        documents = self.document_repo.list()
        ready_documents = {
            document.document_id: document
            for document in documents
            if document.status == "READY"
        }

        if request.document_ids:
            missing = [doc_id for doc_id in request.document_ids if doc_id not in ready_documents]
            if missing:
                raise HTTPException(status_code=404, detail=f"document not found: {missing[0]}")
            active_versions = {
                doc_id: ready_documents[doc_id].active_version for doc_id in request.document_ids
            }
        else:
            active_versions = {
                doc_id: document.active_version for doc_id, document in ready_documents.items()
            }

        if not active_versions:
            return AskResponse(answer="根据当前知识库内容，无法回答该问题。", sources=[])

        query_vector = self.embedding_provider.embed_text(request.question)
        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=request.top_k or DEFAULT_TOP_K,
            document_ids=request.document_ids,
            active_versions=active_versions,
            query_text=request.question,
        )

        useful_results = [result for result in results if result.score >= MIN_SCORE_THRESHOLD]
        if not useful_results:
            return AskResponse(answer="根据当前知识库内容，无法回答该问题。", sources=[])

        prompt = build_qa_prompt(request.question, useful_results)
        answer = self.llm_provider.generate(prompt)
        sources = [
            Source(
                document_id=result.chunk.document_id,
                document=result.chunk.filename,
                chunk_id=result.chunk.chunk_id,
                score=round(result.score, 4),
                content=result.chunk.content,
            )
            for result in useful_results
        ]
        return AskResponse(answer=answer, sources=sources)
