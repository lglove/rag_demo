import hashlib
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile

from app.config import CHUNK_OVERLAP, CHUNK_SIZE
from app.core.schemas import Chunk, Document, UpdateResponse, UploadResponse
from app.core.splitter import split_text
from app.providers.embedding.base import BaseEmbeddingProvider
from app.repositories.document_repo import DocumentRepository
from app.repositories.embedding_cache import EmbeddingCache
from app.vectorstores.base import BaseVectorStore


class DocumentService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        embedding_cache: EmbeddingCache,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
    ) -> None:
        self.document_repo = document_repo
        self.embedding_cache = embedding_cache
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def upload_document(self, file: UploadFile) -> UploadResponse:
        self._validate_file(file.filename)
        text = await self._read_text(file)
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        chunks, embedded_count, reused_count = self._build_chunks(
            document_id=document_id,
            document_version=1,
            filename=file.filename or "untitled.txt",
            text=text,
        )

        document = Document(
            document_id=document_id,
            filename=file.filename or "untitled.txt",
            chunk_count=len(chunks),
            active_version=1,
            status="READY",
            created_at=now,
            updated_at=now,
        )
        self.document_repo.create(document)
        self.vector_store.add_chunks(chunks)

        return UploadResponse(
            document_id=document_id,
            filename=document.filename,
            chunk_count=len(chunks),
            embedded_chunk_count=embedded_count,
            skipped_duplicate_count=reused_count,
        )

    async def update_document(self, document_id: str, file: UploadFile) -> UpdateResponse:
        self._validate_file(file.filename)
        document = self.document_repo.get(document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="document not found")

        old_version = document.active_version
        new_version = old_version + 1
        text = await self._read_text(file)
        chunks, embedded_count, reused_count = self._build_chunks(
            document_id=document_id,
            document_version=new_version,
            filename=file.filename or document.filename,
            text=text,
        )

        self.vector_store.add_chunks(chunks)
        removed_count = self.vector_store.count_by_document(document_id, old_version)

        updated = document.model_copy(
            update={
                "filename": file.filename or document.filename,
                "chunk_count": len(chunks),
                "active_version": new_version,
                "status": "READY",
                "updated_at": datetime.now(timezone.utc),
            }
        )
        self.document_repo.update(updated)
        self.vector_store.delete_by_document(document_id, old_version)

        return UpdateResponse(
            document_id=document_id,
            filename=updated.filename,
            chunk_count=len(chunks),
            embedded_chunk_count=embedded_count,
            reused_embedding_count=reused_count,
            removed_chunk_count=removed_count,
            active_version=new_version,
        )

    def list_documents(self) -> list[Document]:
        return self.document_repo.list()

    def delete_document(self, document_id: str) -> dict[str, int | str]:
        if not self.document_repo.delete(document_id):
            raise HTTPException(status_code=404, detail="document not found")
        removed = self.vector_store.delete_by_document(document_id)
        return {"document_id": document_id, "removed_chunk_count": removed}

    def _build_chunks(
        self,
        document_id: str,
        document_version: int,
        filename: str,
        text: str,
    ) -> tuple[list[Chunk], int, int]:
        pieces = split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        if not pieces:
            raise HTTPException(status_code=400, detail="empty document")

        chunks: list[Chunk] = []
        embedded_count = 0
        reused_count = 0
        for idx, content in enumerate(pieces):
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            embedding = self.embedding_cache.get(content_hash, self.embedding_provider.model_name)
            if embedding is None:
                embedding = self.embedding_provider.embed_text(content)
                self.embedding_cache.set(
                    content_hash,
                    self.embedding_provider.model_name,
                    embedding,
                )
                embedded_count += 1
            else:
                reused_count += 1

            chunks.append(
                Chunk(
                    document_id=document_id,
                    document_version=document_version,
                    chunk_id=idx,
                    filename=filename,
                    content=content,
                    content_hash=content_hash,
                    embedding_model=self.embedding_provider.model_name,
                    embedding=embedding,
                )
            )

        return chunks, embedded_count, reused_count

    async def _read_text(self, file: UploadFile) -> str:
        data = await file.read()
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="file must be utf-8 text") from exc

    def _validate_file(self, filename: str | None) -> None:
        if not filename or not filename.lower().endswith((".txt", ".md")):
            raise HTTPException(status_code=400, detail="only txt and md files are supported")
