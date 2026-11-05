"""Asignaturas y carga de material. Trazabilidad: HU-1 "Carga de material de asignatura"."""

import pytest

from tests.helpers import build_pdf


def test_teacher_creates_subject_and_everyone_lists_it(client, teacher, student, subject):
    listing = client.get("/subjects", headers=student.headers)

    assert listing.status_code == 200
    assert [s["name"] for s in listing.json()] == ["Biologia celular"]
    assert subject["teacher_id"] == str(teacher.user.id)


def test_student_cannot_create_subject(client, student):
    response = client.post("/subjects", json={"name": "X"}, headers=student.headers)

    assert response.status_code == 403


def test_get_unknown_subject_returns_404(client, student):
    response = client.get("/subjects/00000000-0000-4000-8000-000000000000", headers=student.headers)

    assert response.status_code == 404


def test_upload_txt_returns_chunks_created(client, material):
    """Escenario: Carga exitosa de material."""
    assert material["filename"] == "biologia.txt"
    assert material["chunks_created"] >= 2


def test_upload_pdf_is_indexed(client, teacher, subject):
    response = client.post(
        f"/subjects/{subject['id']}/documents",
        files={"file": ("apuntes.pdf", build_pdf("La fotosintesis ocurre en los cloroplastos"), "application/pdf")},
        headers=teacher.headers,
    )

    assert response.status_code == 201
    assert response.json()["chunks_created"] >= 1


def test_uploaded_documents_are_listed_for_the_owner(client, teacher, subject, material):
    response = client.get(f"/subjects/{subject['id']}/documents", headers=teacher.headers)

    assert response.status_code == 200
    assert [d["filename"] for d in response.json()] == ["biologia.txt"]


def test_other_teacher_cannot_upload_to_foreign_subject(client, other_teacher, subject):
    """Escenario: Intento de carga en asignatura ajena (403)."""
    response = client.post(
        f"/subjects/{subject['id']}/documents",
        files={"file": ("a.txt", b"hola", "text/plain")},
        headers=other_teacher.headers,
    )

    assert response.status_code == 403


def test_student_cannot_upload_material(client, student, subject):
    response = client.post(
        f"/subjects/{subject['id']}/documents",
        files={"file": ("a.txt", b"hola", "text/plain")},
        headers=student.headers,
    )

    assert response.status_code == 403


@pytest.mark.parametrize("filename", ["virus.exe", "notas.docx", "sin_extension"])
def test_unsupported_format_is_rejected(client, teacher, subject, filename):
    """Escenario: Formato de archivo no soportado."""
    response = client.post(
        f"/subjects/{subject['id']}/documents",
        files={"file": (filename, b"contenido", "application/octet-stream")},
        headers=teacher.headers,
    )

    assert response.status_code == 415
    assert "PDF, TXT" in response.json()["detail"]


def test_empty_document_returns_422(client, teacher, subject):
    response = client.post(
        f"/subjects/{subject['id']}/documents",
        files={"file": ("vacio.txt", b"   ", "text/plain")},
        headers=teacher.headers,
    )

    assert response.status_code == 422


def test_upload_to_unknown_subject_returns_404(client, teacher):
    response = client.post(
        "/subjects/00000000-0000-4000-8000-000000000000/documents",
        files={"file": ("a.txt", b"hola", "text/plain")},
        headers=teacher.headers,
    )

    assert response.status_code == 404
