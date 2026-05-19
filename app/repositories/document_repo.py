from app.core.schemas import Document
from app.repositories.json_store import JsonStore


class DocumentRepository:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def create(self, document: Document) -> None:
        documents = self.store.load_documents()
        documents.append(document)
        self.store.save_documents(documents)

    def list(self) -> list[Document]:
        return self.store.load_documents()

    def get(self, document_id: str) -> Document | None:
        for document in self.store.load_documents():
            if document.document_id == document_id:
                return document
        return None

    def update(self, document: Document) -> None:
        documents = self.store.load_documents()
        updated = [document if item.document_id == document.document_id else item for item in documents]
        self.store.save_documents(updated)

    def delete(self, document_id: str) -> bool:
        documents = self.store.load_documents()
        kept = [document for document in documents if document.document_id != document_id]
        self.store.save_documents(kept)
        return len(kept) != len(documents)
