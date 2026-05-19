from fastapi import APIRouter, Depends

from app.core.schemas import AskRequest, AskResponse
from app.services.qa_service import QAService

router = APIRouter()


def get_qa_service() -> QAService:
    from app.main import qa_service

    return qa_service


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    service: QAService = Depends(get_qa_service),
) -> AskResponse:
    return service.ask(request)
