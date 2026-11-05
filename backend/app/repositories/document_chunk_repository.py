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
    ) -> list[tuple[DocumentChunk, float]]:
        """Top-k (chunk, distancia coseno) de la asignatura, del más cercano al más lejano (operador <=>)."""
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(DocumentChunk, distance.label("distance"))
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.subject_id == subject_id)
            .order_by(distance)
            .limit(top_k)
        )
        return [(row[0], float(row[1])) for row in db.execute(stmt)]
