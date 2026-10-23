from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.schemas.chat import ChatRequest, ChatResponse, SourceResponse
from app.services.conversation_service import ConversationForbiddenError, ConversationNotFoundError
from app.services.rag_service import LLMUnavailableError, RAGService, SubjectMismatchError
from app.services.subject_service import SubjectNotFoundError

router = APIRouter(prefix="/chat", tags=["Chat"])

rag_service = RAGService()


@router.post("", response_model=ChatResponse)
def chat(user: CurrentUser, data: ChatRequest, db: Session = Depends(get_db)):
    try:
        result = rag_service.answer(db, user.id, data.subject_id, data.message, data.conversation_id)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    except ConversationForbiddenError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="La conversación no es tuya")
    except SubjectMismatchError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La conversación pertenece a otra asignatura",
        )
    except LLMUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El modelo de lenguaje no está disponible en este momento",
        )
    return ChatResponse(
        conversation_id=result.conversation_id,
        answer=result.answer,
        sources=[
            SourceResponse(
                chunk_id=s.chunk_id, document_id=s.document_id, filename=s.filename, fragment=s.fragment
            )
            for s in result.sources
        ],
    )
