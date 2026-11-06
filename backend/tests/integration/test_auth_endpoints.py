"""POST /auth/register y /auth/login contra la BD de test."""


def register(client, **overrides):
    payload = {"name": "Ana", "email": "ana@test.com", "password": "Secreta123!", "role": "student"}
    payload.update(overrides)
    return client.post("/auth/register", json=payload)


def test_register_returns_201_without_password_data(client):
    response = register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@test.com" and body["role"] == "student"
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate_email_returns_409(client):
    register(client)

    assert register(client, name="Otra").status_code == 409


def test_register_duplicate_email_ignores_case(client):
    register(client)

    assert register(client, email="ANA@test.com").status_code == 409


def test_register_validates_input(client):
    assert register(client, email="no-es-un-email").status_code == 422
    assert register(client, password="corta").status_code == 422
    assert register(client, role="admin").status_code == 422


def test_login_returns_bearer_token(client):
    register(client)

    response = client.post("/auth/login", json={"email": "ana@test.com", "password": "Secreta123!"})

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_401(client):
    register(client)

    response = client.post("/auth/login", json={"email": "ana@test.com", "password": "incorrecta1"})

    assert response.status_code == 401


def test_protected_endpoint_requires_token(client):
    assert client.get("/subjects").status_code == 401
    assert client.get("/subjects", headers={"Authorization": "Bearer basura"}).status_code == 401
