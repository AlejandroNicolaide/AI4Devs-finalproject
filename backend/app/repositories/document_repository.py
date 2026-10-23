import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    def create(self, db: Session, document_data: dict) -> Document:
        document = Document(**document_data)
        db.add(document)
        db.flush()
        return document

    def get_by_subject_id(self, db: Session, subject_id: uuid.UUID) -> list[Document]:
        return list(
            db.scalars(
                select(Document).where(Document.subject_id == subject_id).order_by(Document.created_at.desc())
            )
        )

    def get_by_ids(self, db: Session, document_ids: list[uuid.UUID]) -> list[Document]:
        if not document_ids:
            return []
        return list(db.scalars(select(Document).where(Document.id.in_(document_ids))))
