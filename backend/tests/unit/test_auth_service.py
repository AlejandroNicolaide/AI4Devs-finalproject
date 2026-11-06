"""AuthService con el repositorio de usuarios mockeado (prerrequisito de todas las HU)."""

from unittest.mock import MagicMock

import jwt
import pytest

from app.core.config import settings
from app.core.security import hash_password
from app.services.auth_service import AuthService, EmailAlreadyRegisteredError, InvalidCredentialsError


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def service(repo):
    return AuthService(user_repository=repo)


def test_register_hashes_password_and_normalizes_email(service, repo):
    repo.get_by_email.return_value = None

    service.register(
        MagicMock(), {"name": "Ana", "email": "Ana@Test.COM", "password": "Secreta123!", "role": "student"}
    )

    created = repo.create.call_args.args[1]
    assert created["email"] == "ana@test.com"
    assert created["password_hash"] != "Secreta123!"
    assert created["role"] == "student"


def test_register_duplicate_email_raises(service, repo):
    repo.get_by_email.return_value = object()

    with pytest.raises(EmailAlreadyRegisteredError):
        service.register(MagicMock(), {"name": "Ana", "email": "ana@test.com", "password": "x", "role": "student"})

    repo.create.assert_not_called()


def test_login_returns_jwt_with_subject_and_role(service, repo):
    user = MagicMock(id="5f1e1c1e-0000-4000-8000-000000000001", role="teacher")
    user.password_hash = hash_password("Secreta123!")
    repo.get_by_email.return_value = user

    token = service.login(MagicMock(), "Docente@Test.com", "Secreta123!")

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == str(user.id)
    assert payload["role"] == "teacher"
    repo.get_by_email.assert_called_once()
    assert repo.get_by_email.call_args.args[1] == "docente@test.com"


def test_login_wrong_password_raises(service, repo):
    user = MagicMock()
    user.password_hash = hash_password("Secreta123!")
    repo.get_by_email.return_value = user

    with pytest.raises(InvalidCredentialsError):
        service.login(MagicMock(), "ana@test.com", "otra-clave")


def test_login_unknown_user_raises(service, repo):
    repo.get_by_email.return_value = None

    with pytest.raises(InvalidCredentialsError):
        service.login(MagicMock(), "nadie@test.com", "x")
