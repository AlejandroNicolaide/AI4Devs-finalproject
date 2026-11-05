"""ConversationService con el repositorio mockeado. Trazabilidad: HU-3 "Eliminación de historial (GDPR)"."""

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.conversation_service import (
    ConversationForbiddenError,
    ConversationNotFoundError,
    ConversationService,
)

OWNER = uuid.uuid4()
OTHER = uuid.uuid4()


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def service(repo):
    return ConversationService(conversation_repository=repo)


def test_delete_own_conversation(service, repo):
    """Escenario: Eliminación exitosa de una conversación propia."""
    conversation = SimpleNamespace(id=uuid.uuid4(), student_id=OWNER)
    repo.get_by_id.return_value = conversation
    db = MagicMock()

    service.delete_conversation(db, OWNER, conversation.id)

    repo.delete.assert_called_once_with(db, conversation.id)


def test_delete_someone_elses_conversation_is_forbidden(service, repo):
    """Escenario: Intento de eliminar una conversación ajena (403)."""
    repo.get_by_id.return_value = SimpleNamespace(id=uuid.uuid4(), student_id=OTHER)

    with pytest.raises(ConversationForbiddenError):
        service.delete_conversation(MagicMock(), OWNER, uuid.uuid4())

    repo.delete.assert_not_called()


def test_delete_missing_conversation_raises_not_found(service, repo):
    """Escenario: Eliminación de conversación inexistente (404)."""
    repo.get_by_id.return_value = None

    with pytest.raises(ConversationNotFoundError):
        service.delete_conversation(MagicMock(), OWNER, uuid.uuid4())

    repo.delete.assert_not_called()


def test_get_messages_checks_ownership_first(service, repo):
    repo.get_by_id.return_value = SimpleNamespace(id=uuid.uuid4(), student_id=OTHER)

    with pytest.raises(ConversationForbiddenError):
        service.get_messages(MagicMock(), OWNER, uuid.uuid4())

    repo.get_messages.assert_not_called()


def test_list_conversations_delegates_to_repository(service, repo):
    db = MagicMock()
    subject_id = uuid.uuid4()

    service.list_conversations(db, OWNER, subject_id)

    repo.get_by_user.assert_called_once_with(db, OWNER, subject_id)


def test_get_recent_messages_delegates_with_limit(service, repo):
    db = MagicMock()
    conversation_id = uuid.uuid4()

    service.get_recent_messages(db, conversation_id, 6)

    repo.get_recent_messages.assert_called_once_with(db, conversation_id, 6)
