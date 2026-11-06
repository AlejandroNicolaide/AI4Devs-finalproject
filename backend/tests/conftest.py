"""Fixtures compartidas: BD de test Postgres+pgvector, cliente HTTP, usuarios y dobles de LLM/embeddings.

Las variables de entorno se fijan ANTES de importar `app`, porque `settings` y el engine se crean al importar.
"""

import hashlib
import math
import os
import re
from pathlib import Path

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5434/asistenteia_test"
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "clave-solo-para-tests-0123456789abcdef")
os.environ["GEMINI_API_KEY"] = ""  # nunca se llama a Gemini desde los tests
os.environ.pop("SIMILARITY_THRESHOLD", None)
os.environ.pop("LLM_FAKE", None)

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.database import engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.services.auth_service import AuthService  # noqa: E402
from app.services.rag_service import RAGService  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent.parent
EMBEDDING_DIM = 384


class FakeEmbeddings:
    """Embeddings deterministas por bolsa de palabras: textos con palabras en común quedan cerca."""

    @staticmethod
    def _vector(text: str) -> list[float]:
        vec = [0.0] * EMBEDDING_DIM
        for token in re.findall(r"\w+", text.lower()):
            index = int(hashlib.md5(token.encode()).hexdigest(), 16) % EMBEDDING_DIM
            vec[index] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


@pytest.fixture(scope="session", autouse=True)
def _migrated_database():
    """Aplica las migraciones sobre la base de test una vez por sesión."""
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(cfg, "head")
    yield
    engine.dispose()


@pytest.fixture
def db_session(_migrated_database):
    """Sesión ligada a una transacción externa que se revierte al terminar cada test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint", autoflush=False)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def fake_embeddings(request, monkeypatch):
    """Sustituye el modelo HuggingFace salvo en los tests marcados como `slow`."""
    if request.node.get_closest_marker("slow"):
        return None
    fake = FakeEmbeddings()
    monkeypatch.setattr("app.services.document_service.get_embeddings", lambda: fake)
    monkeypatch.setattr("app.services.rag_service.get_embeddings", lambda: fake)
    return fake


@pytest.fixture
def llm_calls(monkeypatch):
    """Sustituye la llamada a Gemini y registra los prompts recibidos."""
    calls: list[list] = []

    def fake_call_llm(prompt):
        calls.append(prompt)
        return "Respuesta simulada del asistente."

    monkeypatch.setattr(RAGService, "_call_llm", staticmethod(fake_call_llm))
    return calls


def _make_user(db_session, name: str, email: str, role: str):
    service = AuthService()
    user = service.register(
        db_session, {"name": name, "email": email, "password": "Password123!", "role": role}
    )
    db_session.flush()
    token = service.login(db_session, email, "Password123!")
    return user, {"Authorization": f"Bearer {token}"}


@pytest.fixture
def teacher(db_session):
    user, headers = _make_user(db_session, "Docente Test", "docente@test.com", "teacher")
    return type("Account", (), {"user": user, "headers": headers})


@pytest.fixture
def other_teacher(db_session):
    user, headers = _make_user(db_session, "Otro Docente", "otro.docente@test.com", "teacher")
    return type("Account", (), {"user": user, "headers": headers})


@pytest.fixture
def student(db_session):
    user, headers = _make_user(db_session, "Estudiante Test", "estudiante@test.com", "student")
    return type("Account", (), {"user": user, "headers": headers})


@pytest.fixture
def other_student(db_session):
    user, headers = _make_user(db_session, "Otro Estudiante", "otro.estudiante@test.com", "student")
    return type("Account", (), {"user": user, "headers": headers})
