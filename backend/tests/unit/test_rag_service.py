"""RAGService con repositorios, servicios y LLM mockeados.

Trazabilidad: HU-2 "Consulta al asistente académico (RAG)".
"""

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.services import rag_service as rag_module
from app.services.conversation_service import ConversationForbiddenError
from app.services.rag_service import (
    HISTORY_MESSAGES,
    NO_MATERIAL_ANSWER,
    NO_RELEVANT_ANSWER,
    LLMUnavailableError,
    RAGService,
    SubjectMismatchError,
)
from app.services.subject_service import SubjectNotFoundError

USER_ID = uuid.uuid4()
SUBJECT_ID = uuid.uuid4()


def make_chunk(content: str, document_id: uuid.UUID):
    return SimpleNamespace(id=uuid.uuid4(), document_id=document_id, content=content)


@pytest.fixture
def deps(monkeypatch):
    document = SimpleNamespace(id=uuid.uuid4(), filename="unidad1.pdf")
    chunks = [make_chunk("La mitosis tiene cuatro fases.", document.id), make_chunk("Profase y metafase.", document.id)]

    conversation = SimpleNamespace(id=uuid.uuid4(), subject_id=SUBJECT_ID)
    conversation_repository = MagicMock()
    conversation_repository.create.return_value = conversation
    conversation_repository.add_message.side_effect = lambda db, cid, role, content: SimpleNamespace(
        id=uuid.uuid4(), role=role, content=content
    )

    chunk_repository = MagicMock()
    chunk_repository.count_by_subject_id.return_value = len(chunks)
    chunk_repository.find_similar.return_value = [(chunks[0], 0.10), (chunks[1], 0.30)]

    document_repository = MagicMock()
    document_repository.get_by_ids.return_value = [document]

    conversation_service = MagicMock()
    conversation_service.get_owned_conversation.return_value = conversation
    conversation_service.get_recent_messages.return_value = []

    embeddings = MagicMock()
    embeddings.embed_query.return_value = [0.1] * 384
    monkeypatch.setattr(rag_module, "get_embeddings", lambda: embeddings)

    service = RAGService(
        chunk_repository=chunk_repository,
        document_repository=document_repository,
        conversation_repository=conversation_repository,
        subject_service=MagicMock(),
        conversation_service=conversation_service,
    )
    return SimpleNamespace(
        service=service,
        db=MagicMock(),
        conversation=conversation,
        chunks=chunks,
        document=document,
        conversation_repository=conversation_repository,
        conversation_service=conversation_service,
        chunk_repository=chunk_repository,
    )


@pytest.fixture
def llm(monkeypatch):
    calls = []

    def fake(prompt):
        calls.append(prompt)
        return "Respuesta del modelo"

    monkeypatch.setattr(RAGService, "_call_llm", staticmethod(fake))
    return calls


def test_answer_with_material_returns_sources_array_and_persists(deps, llm):
    """Escenario: Pregunta con material disponible."""
    result = deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "¿Cuántas fases tiene la mitosis?")

    assert result.answer == "Respuesta del modelo"
    assert isinstance(result.sources, list) and len(result.sources) == 2
    assert {s.filename for s in result.sources} == {"unidad1.pdf"}
    assert result.conversation_id == deps.conversation.id
    roles = [c.args[2] for c in deps.conversation_repository.add_message.call_args_list]
    assert roles == ["user", "assistant"]
    deps.conversation_repository.add_message_sources.assert_called_once()
    deps.db.commit.assert_called_once()


def test_answer_single_chunk_still_returns_array(deps, llm):
    deps.chunk_repository.find_similar.return_value = [(deps.chunks[0], 0.10)]

    result = deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "mitosis")

    assert len(result.sources) == 1


def test_answer_without_material_is_controlled_and_skips_llm(deps, llm):
    """Escenario: Pregunta sin material cargado aún."""
    deps.chunk_repository.count_by_subject_id.return_value = 0

    result = deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "¿Qué es la mitosis?")

    assert result.answer == NO_MATERIAL_ANSWER
    assert result.sources == []
    assert llm == []


def test_prompt_contains_fragments_and_filename(deps, llm):
    deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "¿Cuántas fases tiene la mitosis?")

    prompt = llm[0]
    assert isinstance(prompt[0], SystemMessage)
    assert "unidad1.pdf" in prompt[-1].content
    assert "La mitosis tiene cuatro fases." in prompt[-1].content
    assert "¿Cuántas fases tiene la mitosis?" in prompt[-1].content


def test_unknown_subject_raises(deps, llm):
    deps.service.subject_service.get_subject.side_effect = SubjectNotFoundError("x")

    with pytest.raises(SubjectNotFoundError):
        deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "hola")


def test_conversation_of_another_subject_raises(deps, llm):
    deps.conversation.subject_id = uuid.uuid4()

    with pytest.raises(SubjectMismatchError):
        deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "hola", conversation_id=deps.conversation.id)


def test_conversation_of_another_user_is_rejected(deps, llm):
    deps.conversation_service.get_owned_conversation.side_effect = ConversationForbiddenError()

    with pytest.raises(ConversationForbiddenError):
        deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "hola", conversation_id=uuid.uuid4())


def test_llm_failure_rolls_back_and_raises(deps, monkeypatch):
    def boom(prompt):
        raise LLMUnavailableError("503")

    monkeypatch.setattr(RAGService, "_call_llm", staticmethod(boom))

    with pytest.raises(LLMUnavailableError):
        deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "hola")

    deps.db.rollback.assert_called_once()
    deps.db.commit.assert_not_called()


def test_call_llm_without_api_key_raises_unavailable(monkeypatch):
    monkeypatch.setattr(rag_module.settings, "GEMINI_API_KEY", "")

    with pytest.raises(LLMUnavailableError):
        RAGService._call_llm([HumanMessage(content="hola")])


# --- Historial de la conversación (HU-2: "Continuación de una conversación existente") ---


def test_follow_up_question_sends_previous_messages_to_the_model(deps, llm):
    deps.conversation_service.get_recent_messages.return_value = [
        SimpleNamespace(role="user", content="¿Qué es la mitosis?"),
        SimpleNamespace(role="assistant", content="Es la división celular."),
    ]

    deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "¿Y cuántas fases tiene?", conversation_id=deps.conversation.id)

    prompt = llm[0]
    assert [type(m) for m in prompt] == [SystemMessage, HumanMessage, AIMessage, HumanMessage]
    assert prompt[1].content == "¿Qué es la mitosis?"
    assert prompt[2].content == "Es la división celular."
    assert "¿Y cuántas fases tiene?" in prompt[3].content
    # la pregunta actual aparece una sola vez (el historial se lee antes de persistirla)
    assert sum("¿Y cuántas fases tiene?" in m.content for m in prompt) == 1


def test_history_is_read_with_the_configured_limit(deps, llm):
    deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "otra", conversation_id=deps.conversation.id)

    deps.conversation_service.get_recent_messages.assert_called_once_with(
        deps.db, deps.conversation.id, HISTORY_MESSAGES
    )


def test_first_question_has_no_history(deps, llm):
    deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "primera pregunta")

    deps.conversation_service.get_recent_messages.assert_not_called()
    assert [type(m) for m in llm[0]] == [SystemMessage, HumanMessage]


def test_build_prompt_keeps_history_order():
    history = [("user", "uno"), ("assistant", "dos"), ("user", "tres")]

    prompt = RAGService._build_prompt("cuatro", [("a.txt", "texto")], history)

    assert [m.content for m in prompt[1:-1]] == ["uno", "dos", "tres"]
    assert isinstance(prompt[2], AIMessage)


# --- Umbral de similitud mínimo (HU-2: control de alucinaciones, opcional) ---


def test_without_threshold_all_retrieved_chunks_are_used(deps, llm, monkeypatch):
    """Escenario: Umbral no configurado."""
    monkeypatch.setattr(rag_module.settings, "SIMILARITY_THRESHOLD", None)

    result = deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "mitosis")

    assert len(result.sources) == 2


def test_chunks_below_the_threshold_are_dropped(deps, llm, monkeypatch):
    """Escenario: Algún fragmento supera el umbral (similitudes 0.90 y 0.70, umbral 0.8)."""
    monkeypatch.setattr(rag_module.settings, "SIMILARITY_THRESHOLD", 0.8)

    result = deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "mitosis")

    assert [s.fragment for s in result.sources] == ["La mitosis tiene cuatro fases."]
    assert "Profase y metafase." not in llm[0][-1].content


def test_no_chunk_above_the_threshold_gives_controlled_answer_without_llm(deps, llm, monkeypatch):
    """Escenario: Ningún fragmento supera el umbral."""
    monkeypatch.setattr(rag_module.settings, "SIMILARITY_THRESHOLD", 0.95)

    result = deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "¿Quién ganó el mundial?")

    assert result.answer == NO_RELEVANT_ANSWER
    assert result.sources == []
    assert llm == []
    # la pregunta y la respuesta controlada se guardan igualmente en el historial
    roles = [c.args[2] for c in deps.conversation_repository.add_message.call_args_list]
    assert roles == ["user", "assistant"]


def test_threshold_boundary_is_inclusive(deps, llm, monkeypatch):
    monkeypatch.setattr(rag_module.settings, "SIMILARITY_THRESHOLD", 0.9)
    deps.chunk_repository.find_similar.return_value = [(deps.chunks[0], 0.1)]

    result = deps.service.answer(deps.db, USER_ID, SUBJECT_ID, "mitosis")

    assert len(result.sources) == 1
