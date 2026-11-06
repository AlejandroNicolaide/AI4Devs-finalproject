"""GET /health y CORS configurable (capacidad service-operations)."""

import pytest

from app.core.config import DEFAULT_CORS_ORIGINS, Settings

ENV = {"DATABASE_URL": "postgresql+psycopg2://u:p@h/db", "SECRET_KEY": "k" * 32}


def make_settings(**overrides):
    return Settings(_env_file=None, **ENV, **overrides)


def test_health_returns_ok_without_authentication(client):
    """Escenario: Backend disponible."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_allowed_origin_gets_cors_header(client):
    """Escenario: Origen permitido (por defecto, el frontend local)."""
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_preflight_from_allowed_origin_succeeds(client):
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_unknown_origin_gets_no_cors_header(client):
    """Escenario: Origen no permitido."""
    response = client.get("/health", headers={"Origin": "https://malicioso.example"})

    assert "access-control-allow-origin" not in response.headers


def test_cors_origins_are_read_from_a_comma_separated_variable():
    cfg = make_settings(CORS_ORIGINS="https://app.midominio.com, https://www.midominio.com/ ")

    assert cfg.cors_origins_list == ["https://app.midominio.com", "https://www.midominio.com"]


def test_cors_defaults_to_local_development_origins():
    """Escenario: Sin configuración."""
    assert make_settings().cors_origins_list == DEFAULT_CORS_ORIGINS.split(",")
    assert make_settings(CORS_ORIGINS="").cors_origins_list == DEFAULT_CORS_ORIGINS.split(",")


def test_wildcard_origin_is_never_allowed():
    assert make_settings(CORS_ORIGINS="*").cors_origins_list == DEFAULT_CORS_ORIGINS.split(",")
    assert "*" not in make_settings(CORS_ORIGINS="https://a.com,*").cors_origins_list


@pytest.mark.parametrize("raw, expected", [("", None), ("  ", None), ("0.35", 0.35)])
def test_similarity_threshold_parsing(raw, expected):
    assert make_settings(SIMILARITY_THRESHOLD=raw).SIMILARITY_THRESHOLD == expected


def test_similarity_threshold_is_disabled_by_default():
    assert make_settings().SIMILARITY_THRESHOLD is None


def test_llm_fake_is_disabled_by_default():
    assert make_settings().LLM_FAKE is False
