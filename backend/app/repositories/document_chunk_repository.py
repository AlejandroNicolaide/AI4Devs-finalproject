import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    def create_bulk(self, db: Session, chunks: list[dict]) -> list[DocumentChunk]:
        objs = [DocumentChunk(**c) for c in chunks]
        db.add_all(objs)
        db.flush()
        return objs

    def count_by_subject_id(self, db: Session, subject_id: uuid.UUID) -> int:
        stmt = (
            select(func.count(DocumentChunk.id))
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.subject_id == subject_id)
        )
        return db.scalar(stmt) or 0

    def find_similar(
        self, db: Session, subject_id: uuid.UUID, query_embedding: list[float], top_k: int
    ) -> list[DocumentChunk]:
        """Top-k chunks de la asignatura por distancia coseno (operador <=>)."""
        stmt = (
            select(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.subject_id == subject_id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return list(db.scalars(stmt))
