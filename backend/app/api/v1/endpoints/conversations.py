import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.schemas.conversation import ConversationResponse, MessageResponse
from app.services.conversation_service import (
    ConversationForbiddenError,
    ConversationNotFoundError,
    ConversationService,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])

conversation_service = ConversationService()


@router.get("", response_model=list[ConversationResponse])
def list_conversations(user: CurrentUser, subject_id: uuid.UUID | None = None, db: Session = Depends(get_db)):
    return conversation_service.list_conversations(db, user.id, subject_id)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def get_messages(user: CurrentUser, conversation_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return conversation_service.get_messages(db, user.id, conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    except ConversationForbiddenError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="La conversación no es tuya")


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(user: CurrentUser, conversation_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        conversation_service.delete_conversation(db, user.id, conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada")
    except ConversationForbiddenError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="La conversación no es tuya")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
