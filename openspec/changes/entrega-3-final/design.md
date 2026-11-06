# Design

## Context

Estado observado en la rama `final-project-AN` (creada desde `feature/entrega-2-AN`): backend FastAPI por capas con `RAGService` (`app/services/rag_service.py`), repositorios SQLAlchemy y migraciones Alembic; frontend React 18 + Vite; Postgres 15 + pgvector en `docker-compose.yml`. No hay tests, ni Dockerfiles, ni CI, ni `/health`; CORS está fijo en `main.py`. `RAGService._build_prompt` solo usa la pregunta y los fragmentos; `ConversationRepository.get_messages` ya devuelve los mensajes ordenados. `find_similar` ordena por distancia coseno pero no la devuelve. Ver `proposal.md` para el motivo.

Restricciones de CLAUDE.md que este diseño respeta: capas estrictas (el router no importa models; el repository no llama a services; el service solo importa models bajo `TYPE_CHECKING`), hnsw con coseno, sin secretos en el repo, y archivos solo bajo `backend/app/` y `frontend/src/` para código de aplicación. Los tests, Dockerfiles y CI son infraestructura de soporte y viven fuera de esas carpetas, como ya ocurre con `alembic/` y `docker-compose.yml`.

## Goals / Non-Goals

**Goals:**
- Cubrir los escenarios Gherkin de HU-1/2/3 con tests automáticos repetibles, sin depender de Gemini ni de red.
- Desplegable con un `docker compose` en Dokploy, con HTTPS y dominios propios, y migraciones/seed automáticos.
- Que README y prompts.md describan exactamente lo construido.

**Non-Goals:**
- Consentimiento GDPR, borrado de asignaturas, analítica docente, caché de respuestas, streaming.
- CI/CD de despliegue automático (el deploy lo dispara Dokploy a mano o por webhook; el CI solo valida).
- E2E dentro del CI (se ejecuta en local por el modelo de embeddings y el stack completo).

## Decisions

1. **Historial en el prompt: últimos 6 mensajes, leídos antes de persistir la pregunta nueva.**
   `RAGService` pide el historial a `ConversationService` (que usa `ConversationRepository.get_messages`) antes de `add_message`, así la pregunta actual no aparece duplicada. Se pasan como mensajes `HumanMessage`/`AIMessage` entre el `SystemMessage` y el mensaje con fragmentos. Se recorta en el service a `HISTORY_MESSAGES = 6`. *Alternativa:* resumir el historial con el LLM; descartada por coste y latencia.

2. **Umbral de similitud sobre la distancia coseno, opcional.**
   `find_similar` pasa a devolver pares `(chunk, distancia)`; `RAGService` convierte a similitud (`1 - distancia`) y filtra con `settings.SIMILARITY_THRESHOLD: float | None = None`. Con `None` no filtra, así el comportamiento actual no cambia y no se rompe el seed. Si el filtro deja la lista vacía se responde con un mensaje controlado sin llamar al LLM. *Alternativa:* umbral fijo; descartada porque el valor adecuado depende del material y del idioma, y se calibra con datos reales.

3. **BD de test en Postgres+pgvector, esquema por Alembic, aislamiento por transacción.**
   SQLite no soporta `vector` ni hnsw. Se usa una base `asistenteia_test` en el mismo contenedor (`TEST_DATABASE_URL`), migrada una vez por sesión con `alembic upgrade head` y con un rollback por test (sesión sobre una conexión con transacción externa). Gemini se sustituye por monkeypatch de `RAGService._call_llm` y los embeddings por un vector determinista, para no descargar el modelo de ~460 MB en unitarios; un único test de integración usa el modelo real. *Alternativa:* testcontainers; descartada para no añadir dependencia.

4. **LLM determinista para el E2E: `LLM_FAKE=1`.**
   Una variable de entorno en `Settings` (`LLM_FAKE: bool = False`) hace que `_call_llm` devuelva una respuesta fija derivada del primer fragmento. Solo se activa en el arranque del backend de test; la instancia desplegada no la define. Se documenta como seam de pruebas. *Alternativa:* interceptar Gemini en Playwright; imposible, la llamada sale del backend.

5. **CORS por entorno.** `CORS_ORIGINS` (lista separada por comas) con valor por defecto igual a los dos orígenes locales actuales; `main.py` lo lee de `settings`. Se rechaza `*` combinado con credenciales.

6. **Despliegue: un `docker-compose.prod.yml` de tres servicios.**
   `postgres` (`pgvector/pgvector:pg15`, volumen), `backend` (Python 3.11-slim; el entrypoint corre `alembic upgrade head`, luego `python -m app.seed` y `uvicorn`) y `frontend` (build multistage con `VITE_API_URL` como build-arg, servido por nginx con fallback SPA). El modelo de embeddings se descarga en el build de la imagen para evitar el primer arranque lento. Dokploy enruta `app.<dominio>` y `api.<dominio>` con Let's Encrypt; el healthcheck apunta a `/health`. *Alternativa:* Postgres gestionado de Dokploy; descartada porque no trae pgvector.

7. **CI mínimo en GitHub Actions.** Job backend con servicio `pgvector/pgvector:pg15`, caché de pip y del modelo de HuggingFace, y `pytest`; job frontend con `npm ci`, lint, build y Vitest. Playwright queda fuera del CI.

8. **Versiones fijas.** `requirements.txt` se fija a las versiones que hoy funcionan (`pip freeze` filtrado a las dependencias directas) para evitar que un build futuro se rompa, como ocurrió con SQLAlchemy 2.1.

## Risks / Trade-offs

- [El backend necesita ~1–1,5 GB de RAM por torch + MiniLM; un VPS pequeño puede matarlo por OOM] → comprobar la RAM del VPS antes de desplegar, VPS de 2 GB o más, y límite de memoria visible en Dokploy.
- [La cuota gratuita de Gemini puede devolver 503 si quien revisa pregunta muchas veces seguidas] → ya existe el 503 controlado; avisar en el README.
- [El umbral mal calibrado rechaza preguntas legítimas] → es opcional (`None` por defecto) y se calibra con el material del seed antes de activarlo en producción.
- [El test de integración con embeddings reales es lento] → uno solo, el resto con vectores simulados.
- [Cambiar la firma de `find_similar` afecta a `RAGService` y a los tests] → se cambia en el mismo grupo de tareas que el umbral, con sus tests.
- [El seed en producción deja credenciales de prueba públicas] → es intencional para la revisión (lo exige la guía) y son solo datos de demostración; no se reutilizan secretos reales.

## Migration Plan

1. Desarrollo en `final-project-AN` mediante ramas `feature/tests`, `feature/deploy` y `feature/docs-final`, cada una con su PR hacia `final-project-AN` en el repo propio.
2. Antes del deploy: `docker compose -f docker-compose.prod.yml up --build` en local.
3. Deploy en Dokploy como aplicación Compose; variables definidas en su panel (nunca en el repo).
4. Rollback: redeploy del commit anterior en Dokploy; las migraciones no se modifican (esta entrega no añade migraciones).
