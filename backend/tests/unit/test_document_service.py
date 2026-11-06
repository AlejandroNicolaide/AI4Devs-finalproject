"""DocumentService con repositorios mockeados. Trazabilidad: HU-1 "Carga de material de asignatura"."""

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.document_service import (
    DocumentService,
    EmptyDocumentError,
    NotSubjectOwnerError,
    UnsupportedFileTypeError,
)
from app.services.subject_service import SubjectNotFoundError
from tests.helpers import build_pdf

TEACHER_ID = uuid.uuid4()
SUBJECT_ID = uuid.uuid4()


@pytest.fixture
def repos():
    subject_repository = MagicMock()
    subject_repository.get_by_id.return_value = SimpleNamespace(id=SUBJECT_ID, teacher_id=TEACHER_ID)
    document_repository = MagicMock()
    document_repository.create.return_value = SimpleNamespace(id=uuid.uuid4(), filename="x")
    chunk_repository = MagicMock()
    return SimpleNamespace(
        subject=subject_repository, document=document_repository, chunk=chunk_repository
    )


@pytest.fixture
def service(repos):
    return DocumentService(
        subject_repository=repos.subject, document_repository=repos.document, chunk_repository=repos.chunk
    )


def test_upload_txt_creates_document_and_chunks(service, repos):
    """Escenario: Carga exitosa de material."""
    document, count = service.upload_document(
        MagicMock(), SUBJECT_ID, TEACHER_ID, "unidad1.txt", "La mitosis es una división celular.".encode()
    )

    assert count >= 1
    assert repos.document.create.call_args.args[1] == {"subject_id": SUBJECT_ID, "filename": "unidad1.txt"}
    chunks = repos.chunk.create_bulk.call_args.args[1]
    assert len(chunks) == count
    assert len(chunks[0]["embedding"]) == 384


def test_upload_pdf_extracts_text(service, repos):
    _, count = service.upload_document(
        MagicMock(), SUBJECT_ID, TEACHER_ID, "apuntes.PDF", build_pdf("Fotosintesis y clorofila")
    )

    assert count >= 1
    assert "Fotosintesis" in repos.chunk.create_bulk.call_args.args[1][0]["content"]


def test_txt_falls_back_to_latin1():
    text = DocumentService._extract_text("a.txt", "canción".encode("latin-1"))

    assert text == "canción"


def test_unsupported_extension_is_rejected(service, repos):
    """Escenario: Formato de archivo no soportado."""
    with pytest.raises(UnsupportedFileTypeError):
        service.upload_document(MagicMock(), SUBJECT_ID, TEACHER_ID, "virus.exe", b"MZ")

    repos.document.create.assert_not_called()


def test_empty_document_is_rejected(service, repos):
    with pytest.raises(EmptyDocumentError):
        service.upload_document(MagicMock(), SUBJECT_ID, TEACHER_ID, "vacio.txt", b"   \n  ")

    repos.document.create.assert_not_called()


def test_teacher_who_does_not_own_the_subject_is_rejected(service, repos):
    """Escenario: Intento de carga en asignatura ajena (403)."""
    with pytest.raises(NotSubjectOwnerError):
        service.upload_document(MagicMock(), SUBJECT_ID, uuid.uuid4(), "a.txt", b"hola")

    repos.document.create.assert_not_called()


def test_unknown_subject_raises(service, repos):
    repos.subject.get_by_id.return_value = None

    with pytest.raises(SubjectNotFoundError):
        service.upload_document(MagicMock(), SUBJECT_ID, TEACHER_ID, "a.txt", b"hola")


def test_list_documents_requires_ownership(service, repos):
    with pytest.raises(NotSubjectOwnerError):
        service.list_documents(MagicMock(), SUBJECT_ID, uuid.uuid4())
