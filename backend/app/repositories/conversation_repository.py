import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.message_source import MessageSource


class ConversationRepository:
    def create(self, db: Session, student_id: uuid.UUID, subject_id: uuid.UUID) -> Conversation:
        conversation = Conversation(student_id=student_id, subject_id=subject_id)
        db.add(conversation)
        db.flush()
        return conversation

    def get_by_id(self, db: Session, conversation_id: uuid.UUID) -> Conversation | None:
        return db.get(Conversation, conversation_id)

    def get_by_user(
        self, db: Session, user_id: uuid.UUID, subject_id: uuid.UUID | None = None
    ) -> list[Conversation]:
        stmt = select(Conversation).where(Conversation.student_id == user_id)
        if subject_id is not None:
            stmt = stmt.where(Conversation.subject_id == subject_id)
        return list(db.scalars(stmt.order_by(Conversation.created_at.desc())))

    def get_messages(self, db: Session, conversation_id: uuid.UUID) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.role.desc())
        )
        return list(db.scalars(stmt))

    def add_message(self, db: Session, conversation_id: uuid.UUID, role: str, content: str) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(message)
        db.flush()
        return message

    def add_message_sources(
        self, db: Session, message_id: uuid.UUID, chunk_ids: list[uuid.UUID]
    ) -> list[MessageSource]:
        sources = [MessageSource(message_id=message_id, document_chunk_id=cid) for cid in chunk_ids]
        db.add_all(sources)
        db.flush()
        return sources

    def delete(self, db: Session, conversation_id: uuid.UUID) -> None:
        """Borra la conversación; mensajes y message_sources caen por ON DELETE CASCADE."""
        conversation = db.get(Conversation, conversation_id)
        if conversation is not None:
            db.delete(conversation)
            db.commit()
