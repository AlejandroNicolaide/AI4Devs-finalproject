from __future__ import annotations

from typing import TYPE_CHECKING

import io
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session

from app.core.embeddings import get_embeddings
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.subject_repository import SubjectRepository
from app.services.subject_service import SubjectNotFoundError

if TYPE_CHECKING:
    from app.models.document import Document

SUPPORTED_EXTENSIONS = (".pdf", ".txt")


class NotSubjectOwnerError(Exception):
    pass


class UnsupportedFileTypeError(Exception):
    pass


class EmptyDocumentError(Exception):
    pass


class DocumentService:
    def __init__(
        self,
        subject_repository: SubjectRepository | None = None,
        document_repository: DocumentRepository | None = None,
        chunk_repository: DocumentChunkRepository | None = None,
    ):
        self.subject_repository = subject_repository or SubjectRepository()
        self.document_repository = document_repository or DocumentRepository()
        self.chunk_repository = chunk_repository or DocumentChunkRepository()
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def _get_owned_subject(self, db: Session, subject_id: uuid.UUID, teacher_id: uuid.UUID):
        subject = self.subject_repository.get_by_id(db, subject_id)
        if subject is None:
            raise SubjectNotFoundError(str(subject_id))
        if subject.teacher_id != teacher_id:
            raise NotSubjectOwnerError()
        return subject

    @staticmethod
    def _has_content_beyond_repeated_lines(pages: list[str]) -> bool:
        """False si, quitando las líneas repetidas en más de la mitad de las páginas, no queda texto."""
        page_lines = [{line.strip() for line in text.splitlines() if line.strip()} for text in pages]
        if len(pages) < 2:
            return any(page_lines)
        counts: dict[str, int] = {}
        for lines in page_lines:
            for line in lines:
                counts[line] = counts.get(line, 0) + 1
        return any(count <= len(pages) / 2 for count in counts.values())

    @staticmethod
    def _extract_text(filename: str, content: bytes) -> str:
        name = filename.lower()
        if name.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            if not DocumentService._has_content_beyond_repeated_lines(pages):
                # p. ej. un escaneo (CamScanner...): solo tiene texto la marca de agua repetida en cada página
                raise EmptyDocumentError(filename)
            return "\n".join(pages)
        if name.endswith(".txt"):
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return content.decode("latin-1")
        raise UnsupportedFileTypeError(filename)

    def upload_document(
        self, db: Session, subject_id: uuid.UUID, teacher_id: uuid.UUID, filename: str, content: bytes
    ) -> tuple[Document, int]:
        self._get_owned_subject(db, subject_id, teacher_id)
        if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
            raise UnsupportedFileTypeError(filename)

        text = self._extract_text(filename, content).strip()
        if not text:
            raise EmptyDocumentError(filename)

        pieces = self.splitter.split_text(text)
        embeddings = get_embeddings().embed_documents(pieces)

        document = self.document_repository.create(db, {"subject_id": subject_id, "filename": filename})
        self.chunk_repository.create_bulk(
            db,
            [
                {"document_id": document.id, "content": piece, "embedding": emb}
                for piece, emb in zip(pieces, embeddings)
            ],
        )
        db.commit()
        db.refresh(document)
        return document, len(pieces)

    def list_documents(self, db: Session, subject_id: uuid.UUID, teacher_id: uuid.UUID) -> list[Document]:
        self._get_owned_subject(db, subject_id, teacher_id)
        return self.document_repository.get_by_subject_id(db, subject_id)
