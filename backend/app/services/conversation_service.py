import uuid

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository


class ConversationNotFoundError(Exception):
    pass


class ConversationForbiddenError(Exception):
    pass


class ConversationService:
    def __init__(self, conversation_repository: ConversationRepository | None = None):
        self.conversation_repository = conversation_repository or ConversationRepository()

    def get_owned_conversation(
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> Conversation:
        conversation = self.conversation_repository.get_by_id(db, conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(str(conversation_id))
        if conversation.student_id != user_id:
            raise ConversationForbiddenError()
        return conversation

    def list_conversations(
        self, db: Session, user_id: uuid.UUID, subject_id: uuid.UUID | None = None
    ) -> list[Conversation]:
        return self.conversation_repository.get_by_user(db, user_id, subject_id)

    def get_messages(self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> list[Message]:
        self.get_owned_conversation(db, user_id, conversation_id)
        return self.conversation_repository.get_messages(db, conversation_id)

    def delete_conversation(self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
        self.get_owned_conversation(db, user_id, conversation_id)
        self.conversation_repository.delete(db, conversation_id)
