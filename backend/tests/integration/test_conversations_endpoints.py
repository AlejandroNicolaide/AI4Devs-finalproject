"""Historial y borrado de conversaciones. Trazabilidad: HU-3 "Eliminación de historial (GDPR)"."""

import uuid

from sqlalchemy import text


def start_conversation(client, student, subject):
    response = client.post(
        "/chat", json={"subject_id": subject["id"], "message": "¿Qué es la mitosis?"}, headers=student.headers
    )
    assert response.status_code == 200
    return response.json()["conversation_id"]


def test_list_conversations_returns_only_the_owners(client, student, other_student, subject, material, llm_calls):
    mine = start_conversation(client, student, subject)
    start_conversation(client, other_student, subject)

    response = client.get("/conversations", headers=student.headers)

    assert [c["id"] for c in response.json()] == [mine]


def test_list_conversations_can_filter_by_subject(client, teacher, student, subject, material, llm_calls):
    start_conversation(client, student, subject)
    other = client.post("/subjects", json={"name": "Otra"}, headers=teacher.headers).json()

    response = client.get("/conversations", params={"subject_id": other["id"]}, headers=student.headers)

    assert response.json() == []


def test_messages_are_returned_for_the_owner(client, student, subject, material, llm_calls):
    conversation_id = start_conversation(client, student, subject)

    response = client.get(f"/conversations/{conversation_id}/messages", headers=student.headers)

    assert response.status_code == 200
    assert [m["role"] for m in response.json()] == ["user", "assistant"]
    assert response.json()[0]["content"] == "¿Qué es la mitosis?"


def test_delete_own_conversation_removes_messages_and_sources(client, student, subject, material, llm_calls, db_session):
    """Escenario: Eliminación exitosa de una conversación propia."""
    conversation_id = start_conversation(client, student, subject)
    assert db_session.scalar(text("select count(*) from message_sources")) >= 1

    response = client.delete(f"/conversations/{conversation_id}", headers=student.headers)

    assert response.status_code == 204
    assert db_session.scalar(text("select count(*) from conversations")) == 0
    assert db_session.scalar(text("select count(*) from messages")) == 0
    assert db_session.scalar(text("select count(*) from message_sources")) == 0
    # la eliminación no puede deshacerse: el historial ya no se puede leer
    assert client.get(f"/conversations/{conversation_id}/messages", headers=student.headers).status_code == 404


def test_deleting_a_conversation_keeps_the_material(client, student, subject, material, llm_calls, db_session):
    conversation_id = start_conversation(client, student, subject)

    client.delete(f"/conversations/{conversation_id}", headers=student.headers)

    assert db_session.scalar(text("select count(*) from document_chunks")) >= 1


def test_delete_someone_elses_conversation_returns_403(
    client, student, other_student, subject, material, llm_calls, db_session
):
    """Escenario: Intento de eliminar una conversación ajena."""
    conversation_id = start_conversation(client, student, subject)

    response = client.delete(f"/conversations/{conversation_id}", headers=other_student.headers)

    assert response.status_code == 403
    assert db_session.scalar(text("select count(*) from conversations")) == 1


def test_delete_unknown_conversation_returns_404(client, student):
    """Escenario: Eliminación de conversación inexistente."""
    response = client.delete(f"/conversations/{uuid.uuid4()}", headers=student.headers)

    assert response.status_code == 404


def test_read_someone_elses_messages_returns_403(client, student, other_student, subject, material, llm_calls):
    conversation_id = start_conversation(client, student, subject)

    response = client.get(f"/conversations/{conversation_id}/messages", headers=other_student.headers)

    assert response.status_code == 403


def test_conversations_require_authentication(client):
    assert client.get("/conversations").status_code == 401
    assert client.delete(f"/conversations/{uuid.uuid4()}").status_code == 401
