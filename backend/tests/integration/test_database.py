"""Comportamiento a nivel de base de datos: índice vectorial, cascadas y recorte del historial."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository


def test_hnsw_index_exists_with_cosine_ops(db_session):
    definition = db_session.scalar(
        text("select indexdef from pg_indexes where indexname = 'ix_document_chunks_embedding_hnsw'")
    )

    assert definition is not None
    assert "hnsw" in definition and "vector_cosine_ops" in definition


def test_find_similar_orders_by_cosine_distance_within_the_subject(
    client, teacher, subject, material, db_session, fake_embeddings
):
    other = client.post("/subjects", json={"name": "Otra"}, headers=teacher.headers).json()
    client.post(
        f"/subjects/{other['id']}/documents",
        files={"file": ("ajeno.txt", b"mitosis mitosis mitosis fases", "text/plain")},
        headers=teacher.headers,
    )

    query = fake_embeddings.embed_query("fases profase metafase anafase telofase de la mitosis")
    found = DocumentChunkRepository().find_similar(db_session, uuid.UUID(subject["id"]), query, 5)

    chunks = [c for c, _ in found]
    distances = [d for _, d in found]
    assert "profase" in chunks[0].content
    assert distances == sorted(distances) and 0 <= distances[0] < distances[-1] <= 1
    # nunca devuelve fragmentos de otra asignatura
    assert all("ajeno" not in c.content for c in chunks)
    assert len(found) == material["chunks_created"]


def test_deleting_a_subject_cascades_to_documents_and_chunks(client, teacher, subject, material, db_session):
    assert db_session.scalar(text("select count(*) from document_chunks")) == material["chunks_created"]

    db_session.execute(text("delete from subjects where id = :id"), {"id": subject["id"]})

    assert db_session.scalar(text("select count(*) from documents")) == 0
    assert db_session.scalar(text("select count(*) from document_chunks")) == 0


def test_deleting_a_message_cascades_to_its_sources(client, student, subject, material, llm_calls, db_session):
    client.post(
        "/chat", json={"subject_id": subject["id"], "message": "mitosis fases"}, headers=student.headers
    )
    assert db_session.scalar(text("select count(*) from message_sources")) >= 1

    db_session.execute(text("delete from messages"))

    assert db_session.scalar(text("select count(*) from message_sources")) == 0


def test_get_recent_messages_returns_the_last_n_in_chronological_order(client, student, subject, db_session):
    conversation = Conversation(student_id=student.user.id, subject_id=uuid.UUID(subject["id"]))
    other = Conversation(student_id=student.user.id, subject_id=uuid.UUID(subject["id"]))
    db_session.add_all([conversation, other])
    db_session.flush()
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for turn in range(5):  # 5 turnos = 10 mensajes
        moment = start + timedelta(minutes=turn)
        db_session.add(Message(conversation_id=conversation.id, role="user", content=f"p{turn}", created_at=moment))
        db_session.add(
            Message(conversation_id=conversation.id, role="assistant", content=f"r{turn}", created_at=moment)
        )
    db_session.add(Message(conversation_id=other.id, role="user", content="ajeno", created_at=start))
    db_session.flush()

    recent = ConversationRepository().get_recent_messages(db_session, conversation.id, 6)

    assert [m.content for m in recent] == ["p2", "r2", "p3", "r3", "p4", "r4"]

