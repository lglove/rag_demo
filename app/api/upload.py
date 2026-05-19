from fastapi import APIRouter, Depends, UploadFile

from app.core.schemas import Document, UpdateResponse, UploadResponse
from app.services.document_service import DocumentService

router = APIRouter()


def get_document_service() -> DocumentService:
    from app.main import document_service

    return document_service


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile,
    service: DocumentService = Depends(get_document_service),
) -> UploadResponse:
    return await service.upload_document(file)


@router.get("/documents", response_model=list[Document])
def list_documents(service: DocumentService = Depends(get_document_service)) -> list[Document]:
    return service.list_documents()


@router.put("/documents/{document_id}", response_model=UpdateResponse)
async def update_document(
    document_id: str,
    file: UploadFile,
    service: DocumentService = Depends(get_document_service),
) -> UpdateResponse:
    return await service.update_document(document_id, file)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
) -> dict[str, int | str]:
    return service.delete_document(document_id)
