# Tasks

## 1. Higiene del repo y andamiaje de ramas

- [x] 1.1 Añadir a `.gitignore` `*.log`, `.agents/`, `.claude/`, `entrega.md`, los `.md` de lecciones y el PDF de la devolución; verificar con `git status` que solo quedan archivos del proyecto como candidatos a commit
- [x] 1.2 Verificar que no hay `.env` ni claves versionadas: `git ls-files | grep -i "\.env$"` vacío y `git grep -n "AIza"` sin resultados
- [x] 1.3 Commitear el change `entrega-3-final` (artefactos OpenSpec) en `final-project-AN` y publicar la rama; verificar con `git log origin/final-project-AN`
- [x] 1.4 Crear `feature/tests` desde `final-project-AN`; verificar con `git branch --show-current`

## 2. Historial de conversación en las respuestas (HU-2)

- [x] 2.1 Añadir en `ConversationService` un método de historial reciente (últimos 6 mensajes) y usarlo desde `RAGService` antes de persistir la pregunta nueva; verificar que `/chat` sigue respondiendo con `sources` como array
- [x] 2.2 Incluir el historial como mensajes previos en `RAGService._build_prompt`; verificar con un test unitario que la pregunta actual no aparece duplicada y que sin `conversation_id` no hay historial
- [x] 2.3 Test unitario del recorte a 6 mensajes y de que solo se usa el historial de esa conversación (escenarios "Pregunta de seguimiento", "Primera pregunta sin historial" e "Historial acotado")

## 3. Infraestructura de tests backend

- [x] 3.1 Crear `backend/requirements-dev.txt` (`pytest`, `pytest-cov`, `httpx`) y `backend/pytest.ini`; verificar `pytest --collect-only` sin errores
- [x] 3.2 Crear la base `asistenteia_test` (documentado en el README) y `backend/tests/conftest.py` con `TEST_DATABASE_URL`, `alembic upgrade head` por sesión, sesión con rollback por test, override de `get_db` y `TestClient`; verificar con un test trivial que lee la tabla `users`
- [x] 3.3 Fixtures de docente, estudiante, token, asignatura y documento con vectores deterministas, y doble de `RAGService._call_llm`; verificar que ningún test llama a Gemini ni descarga el modelo salvo el marcado como lento

## 4. Tests unitarios backend (trazados a los Gherkin)

- [x] 4.1 `AuthService`: registro, email duplicado, login correcto e inválido; verificar `pytest tests/unit/test_auth_service.py` en verde
- [x] 4.2 `RAGService`: HU-2 con material (sources array y persistencia), sin material (no llama al LLM), asignatura inexistente, `SubjectMismatchError`, rollback ante `LLMUnavailableError`; verificar en verde
- [x] 4.3 `DocumentService`: HU-1 extensión no soportada, documento vacío, TXT utf-8 y latin-1, PDF (fixture pequeño en `tests/fixtures/`), docente no titular (403); verificar en verde
- [x] 4.4 `ConversationService`: HU-3 propiedad, borrado, 404 y 403; verificar en verde

## 5. Tests de integración backend

- [x] 5.1 Auth: `/auth/register` 201/409/422 y `/auth/login` 200/401; verificar en verde
- [x] 5.2 Subjects + documents: crear asignatura, subir TXT y PDF con `chunks_created`, 403 en asignatura ajena, 415 en formato no soportado y 422 en documento vacío
- [x] 5.3 Chat: 401 sin token, respuesta con `sources` como array, camino sin material, conversación existente; verificar que el historial llega al doble del LLM
- [x] 5.4 Conversations: listado, mensajes del propietario, `DELETE` 204 con cascada a mensajes y `message_sources`, 403 ajena, 404 inexistente
- [x] 5.5 Cascada a nivel BD asignatura → documentos → fragmentos (criterio del ticket 3); verificar borrando la asignatura por SQL
- [x] 5.6 Ejecutar `pytest --cov=app` y verificar que todo pasa; guardar el porcentaje para el README

## 6. Operación del servicio y umbral anti-alucinaciones

- [x] 6.1 Añadir `CORS_ORIGINS` y `SIMILARITY_THRESHOLD` a `Settings` y a `.env.example`; usar `CORS_ORIGINS` en `main.py`; verificar con tests de los escenarios "Origen permitido", "Origen no permitido" y "Sin configuración"
- [x] 6.2 Añadir `GET /health`; verificar con un test que responde 200 `{"status": "ok"}` sin token
- [x] 6.3 `DocumentChunkRepository.find_similar` devuelve `(chunk, distancia)` y `RAGService` aplica el umbral con respuesta controlada sin llamar al LLM; verificar con tests de los tres escenarios del umbral
- [x] 6.4 Calibrar `SIMILARITY_THRESHOLD` con el material del seed (pregunta relevante vs. ajena) y registrar el valor recomendado en el README

## 7. Tests frontend (Vitest + RTL)

- [x] 7.1 Instalar `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`; crear `vitest.config.ts`, `src/setupTests.ts` y el script `test`; verificar `npm run test` con un test de humo
- [x] 7.2 Tests de `MessageBubble` (chips de fuentes expandibles) y `ChatWindow` (envío, indicador "escribiendo…", mensaje de asignatura sin material); verificar en verde
- [x] 7.3 Tests de `LoginPage` (error con credenciales inválidas) y `FileUpload` (rechazo de formatos no soportados); verificar en verde
- [x] 7.4 Verificar `npm run lint` y `npm run build` sin errores

## 8. Test E2E con Playwright

- [x] 8.1 Añadir `LLM_FAKE` a `Settings` y a `_call_llm` (solo test, desactivado por defecto) con un test unitario; instalar `@playwright/test` y crear `playwright.config.ts`
- [x] 8.2 Spec `e2e/chat-flow.spec.ts`: docente crea asignatura y sube un TXT → estudiante pregunta → la respuesta muestra "Fuentes" → historial → eliminar; verificar `npx playwright test` en verde con el stack local y `LLM_FAKE=1`
- [x] 8.3 Documentar los prerrequisitos y el comando del E2E en el README (sección Pruebas)

## 9. CI y PR de tests

- [x] 9.1 Crear `.github/workflows/ci.yml` (job backend con servicio pgvector y job frontend); verificar que el workflow queda en verde en GitHub
- [x] 9.2 Subir `feature/tests`, abrir el PR hacia `final-project-AN` en el repo propio (base correcta, no el repo de LIDR) y ejecutar `/code-review` sobre él; verificar el PR abierto y las observaciones tratadas

## 10. Despliegue en Dokploy

- [x] 10.1 Crear `feature/deploy` desde `final-project-AN`; fijar versiones en `requirements.txt` y verificar con `pip install -r requirements.txt` en un venv limpio y `pytest` en verde
- [x] 10.2 `backend/Dockerfile` y entrypoint (migraciones → seed → uvicorn) con precarga del modelo de embeddings; verificar `docker build` y que `/health` responde en el contenedor
- [x] 10.3 `frontend/Dockerfile` (multistage, `VITE_API_URL` como build-arg) y `frontend/nginx.conf` con fallback SPA; verificar `docker build` y que la SPA carga y navega por URL directa
- [x] 10.4 `docker-compose.prod.yml` (`pgvector/pgvector:pg15`, backend, frontend, volumen, healthchecks); verificar `docker compose -f docker-compose.prod.yml up --build` en local con login y pregunta con fuentes
- [x] 10.5 Redactar la guía de Dokploy en el README: variables exactas (`DATABASE_URL`, `SECRET_KEY`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `CORS_ORIGINS`, `VITE_API_URL`, `POSTGRES_*`), dominios `app.` y `api.` con HTTPS, requisito de RAM y uso de `scripts/init_db.sql`; verificar que cada variable existe en `config.py` o en los compose
- [x] 10.6 Subir `feature/deploy`, abrir el PR hacia `final-project-AN` y ejecutar `/code-review`; verificar el PR
- [ ] 10.7 (Lo ejecuta el usuario en su VPS) Desplegar en Dokploy y comprobar `https://api.<dominio>/health` y el flujo con credenciales del seed; registrar la URL pública

## 11. Documentación final

- [x] 11.1 Crear `feature/docs-final` desde `final-project-AN` actualizada
- [ ] 11.2 (pendiente solo la URL pública del punto 0.4) README: URL pública (0.4), instalación y Docker (1.4), estructura real (2.3), infraestructura y CI reales (2.4), seguridad sin el consentimiento en el primer login y con HTTPS (2.5), tests reales y sección "Pruebas" con cobertura (2.6), numeración de la sección 4, nice-to-have del umbral (1.2) y PRs reales (7); verificar con una lectura contra el código que cada afirmación es cierta
- [x] 11.3 `prompts.md`: secciones de tests, despliegue y mantenimiento (máximo 3 prompts por sección), tabla "IA por fase" con las 6 fases y resumen del flujo de IA (herramientas, modelos, contexto y ajustes humanos); verificar que no quedan textos de plantilla
- [x] 11.4 Subir `feature/docs-final`, abrir el PR hacia `final-project-AN` y ejecutar `/code-review`; verificar el PR

## 12. Cierre e integración

- [x] 12.1 Fusionar los tres PRs en `final-project-AN` y ejecutar en limpio `pytest`, `npm run test`, `npm run build` y el E2E; verificar todo en verde
- [x] 12.2 Recorrer el checklist de la Lección 3 contra la rama remota (README, prompts.md, 3-5 funcionalidades, tests, evidencia, sin secretos, nombre de rama `final-project-AN`) y anotar el resultado

## Workflow follow-up

- Archivar el change (`/opsx:archive`) y sincronizar las specs `rag-chat` y `service-operations` tras fusionar los PRs.
- El usuario completa el Typeform con `https://github.com/AlejandroNicolaide/AI4Devs-finalproject/tree/final-project-AN` (tipo "final", sin URL de PR).
- `entrega.md` permanece local y sin commit.
