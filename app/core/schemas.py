from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Document(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    active_version: int = 1
    status: str = "READY"
    created_at: datetime
    updated_at: datetime


class Chunk(BaseModel):
    document_id: str
    document_version: int
    chunk_id: int
    filename: str
    content: str
    content_hash: str
    embedding_model: str
    embedding: list[float]


class Source(BaseModel):
    document_id: str
    document: str
    chunk_id: int
    score: float
    content: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    document_ids: Optional[list[str]] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    embedded_chunk_count: int
    skipped_duplicate_count: int


class UpdateResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    embedded_chunk_count: int
    reused_embedding_count: int
    removed_chunk_count: int
    active_version: int


class SearchResult(BaseModel):
    chunk: Chunk
    score: float
