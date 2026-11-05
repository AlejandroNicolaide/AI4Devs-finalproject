"""POST /chat con BD real y LLM/embeddings simulados. Trazabilidad: HU-2 "Consulta al asistente (RAG)"."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def ask(client, student, subject, message, conversation_id=None):
    payload = {"subject_id": subject["id"], "message": message}
    if conversation_id:
        payload["conversation_id"] = conversation_id
    return client.post("/chat", json=payload, headers=student.headers)


def test_chat_requires_authentication(client, subject):
    response = client.post("/chat", json={"subject_id": subject["id"], "message": "hola"})

    assert response.status_code == 401


def test_question_with_material_returns_answer_and_sources_array(client, student, subject, material, llm_calls):
    """Escenario: Pregunta con material disponible."""
    response = ask(client, student, subject, "¿Cuáles son las fases de la mitosis?")

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Respuesta simulada del asistente."
    assert isinstance(body["sources"], list) and len(body["sources"]) >= 1
    assert set(body["sources"][0]) == {"chunk_id", "document_id", "filename", "fragment"}
    assert body["sources"][0]["filename"] == "biologia.txt"
    assert len(llm_calls) == 1


def test_sources_are_ordered_by_similarity(client, student, subject, material, llm_calls):
    body = ask(client, student, subject, "fases profase metafase anafase telofase mitosis").json()

    assert "mitosis" in body["sources"][0]["fragment"].lower()


def test_question_without_material_is_controlled(client, student, subject, llm_calls):
    """Escenario: Pregunta sin material cargado aún."""
    response = ask(client, student, subject, "¿Qué es la mitosis?")

    assert response.status_code == 200
    body = response.json()
    assert "todavía no tiene material" in body["answer"]
    assert body["sources"] == []
    assert llm_calls == []


def test_first_question_creates_conversation_and_follow_up_reuses_it(
    client, student, subject, material, llm_calls
):
    first = ask(client, student, subject, "¿Qué es la fotosintesis?").json()

    follow_up = ask(client, student, subject, "¿Y dónde ocurre?", first["conversation_id"]).json()

    assert follow_up["conversation_id"] == first["conversation_id"]
    messages = client.get(f"/conversations/{first['conversation_id']}/messages", headers=student.headers).json()
    assert [m["role"] for m in messages].count("user") == 2
    assert [m["role"] for m in messages].count("assistant") == 2


def test_follow_up_sends_the_previous_turn_to_the_model(client, student, subject, material, llm_calls):
    """Escenario: Continuación de una conversación existente."""
    first = ask(client, student, subject, "¿Qué es la fotosintesis?").json()

    ask(client, student, subject, "¿Y dónde ocurre?", first["conversation_id"])

    prompt = llm_calls[1]
    assert [type(m) for m in prompt] == [SystemMessage, HumanMessage, AIMessage, HumanMessage]
    assert prompt[1].content == "¿Qué es la fotosintesis?"
    assert prompt[2].content == "Respuesta simulada del asistente."
    assert "¿Y dónde ocurre?" in prompt[3].content


def test_conversation_of_another_user_returns_403(client, student, other_student, subject, material, llm_calls):
    first = ask(client, student, subject, "hola").json()

    response = ask(client, other_student, subject, "intruso", first["conversation_id"])

    assert response.status_code == 403


def test_conversation_of_another_subject_returns_400(client, teacher, student, subject, material, llm_calls):
    first = ask(client, student, subject, "hola").json()
    other = client.post("/subjects", json={"name": "Otra"}, headers=teacher.headers).json()

    response = ask(client, student, other, "hola", first["conversation_id"])

    assert response.status_code == 400


def test_unknown_subject_returns_404(client, student, llm_calls):
    response = ask(client, student, {"id": "00000000-0000-4000-8000-000000000000"}, "hola")

    assert response.status_code == 404


def test_empty_message_is_rejected(client, student, subject):
    assert ask(client, student, subject, "").status_code == 422


def test_gemini_unavailable_returns_503_and_leaves_no_conversation(client, student, subject, material):
    """Sin GEMINI_API_KEY (como en los tests) el LLM no está disponible: respuesta 503 limpia."""
    response = ask(client, student, subject, "¿Qué es la mitosis?")

    assert response.status_code == 503
    assert client.get("/conversations", headers=student.headers).json() == []
