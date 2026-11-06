import pytest

PARAGRAPHS = [
    "La mitosis es el proceso de division celular que da lugar a dos celulas hijas geneticamente identicas. "
    "Sus fases son profase, metafase, anafase y telofase y ocurre en las celulas somaticas del organismo. " * 2,
    "La fotosintesis convierte la energia de la luz solar en energia quimica dentro de los cloroplastos. "
    "La clorofila absorbe la luz roja y azul y la planta produce glucosa y oxigeno a partir de agua y dioxido de carbono. " * 2,
    "La respiracion celular ocurre en las mitocondrias y degrada la glucosa para producir ATP. "
    "Sus etapas son la glucolisis, el ciclo de Krebs y la cadena de transporte de electrones en presencia de oxigeno. " * 2,
    "El nucleo celular contiene el ADN organizado en cromosomas y controla la expresion genetica de la celula. "
    "Durante la division el material genetico se duplica y se reparte de forma equitativa entre las celulas hijas. " * 2,
]
MATERIAL = "\n\n".join(PARAGRAPHS)


@pytest.fixture
def subject(client, teacher):
    response = client.post(
        "/subjects", json={"name": "Biologia celular", "description": "Demo"}, headers=teacher.headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def material(client, teacher, subject):
    """Sube un TXT con varios fragmentos a la asignatura y devuelve la respuesta de la carga."""
    response = client.post(
        f"/subjects/{subject['id']}/documents",
        files={"file": ("biologia.txt", MATERIAL.encode(), "text/plain")},
        headers=teacher.headers,
    )
    assert response.status_code == 201
    return response.json()
