# Proposal

## Why

La Entrega 2 dejó el MVP funcionando en local, pero la entrega final (10-11-2026) exige además una suite de tests (unitarios, integración y un E2E), evidencia de funcionamiento mediante una URL pública, un README fiel a lo construido y un `prompts.md` completo. Hoy no hay ningún test, no hay despliegue, el README promete cosas que no existen (CI/CD con GitHub Actions, consentimiento en el primer login, despliegue en Vercel/Render/Supabase) y un criterio de aceptación de la HU-2 (la respuesta tiene en cuenta el historial de la conversación) no está implementado. La devolución de LIDR a la Entrega 1 también sugiere el umbral de similitud contra alucinaciones y pide IA en al menos 4 de las 6 fases.

## What Changes

- **Historial en las respuestas:** el prompt del chat incluye los últimos mensajes de la conversación.
- **Umbral anti-alucinaciones (opcional, tras lo obligatorio):** `SIMILARITY_THRESHOLD` configurable; si ningún fragmento lo supera, respuesta controlada sin llamar al LLM.
- **Operación del servicio:** endpoint `GET /health` y orígenes CORS configurables por variable de entorno (`CORS_ORIGINS`) en lugar de la lista fija.
- **Tests backend (Pytest):** unitarios del Service Layer con mocks e integración de endpoints contra una BD de test Postgres+pgvector, trazados a los escenarios Gherkin de las HU.
- **Tests frontend (Vitest + React Testing Library)** de los componentes clave.
- **E2E (Playwright):** flujo docente sube material → estudiante pregunta → respuesta con fuentes → historial → borrado, con un LLM determinista (`LLM_FAKE=1`) solo para tests.
- **CI mínimo:** workflow de GitHub Actions con pytest (servicio pgvector) y lint/build/Vitest.
- **Despliegue en Dokploy:** Dockerfiles de backend y frontend, `docker-compose.prod.yml` con `pgvector/pgvector:pg15`, versiones fijas en `requirements.txt` y guía con las variables de entorno.
- **Documentación:** README (URL pública, sección Pruebas, 2.3/2.4/2.5/2.6 y 4 corregidas, PRs reales) y `prompts.md` ampliado con la tabla de IA por fase; higiene del `.gitignore`.

No hay cambios incompatibles de API. El consentimiento GDPR en el primer login no se implementa: se ajusta el README.

## Capabilities

### New Capabilities
- `service-operations`: comprobación de salud del backend (`GET /health`) y política CORS configurable por entorno, necesarios para desplegar detrás de un dominio propio.

### Modified Capabilities
- `rag-chat`: el prompt incorpora el historial reciente de la conversación y, opcionalmente, un umbral de similitud mínimo que activa una respuesta controlada cuando no hay fragmentos relevantes.

## Impact

- **Backend:** `app/services/rag_service.py`, `app/repositories/document_chunk_repository.py`, `app/core/config.py`, `app/main.py`, `requirements.txt`; nuevo `tests/` y `requirements-dev.txt`; `Dockerfile`.
- **Frontend:** `package.json` (Vitest, Playwright), `Dockerfile`, `nginx.conf`, tests y specs E2E.
- **Raíz:** `docker-compose.prod.yml`, `.github/workflows/ci.yml`, `.gitignore`, `readme.md`, `prompts.md`.
- **Infraestructura:** VPS con Dokploy y dominio propio; el backend necesita unos 2 GB de RAM por el modelo de embeddings local.
- **Fuera de alcance:** consentimiento GDPR, endpoint de borrado de asignatura, analítica docente, integración con Moodle.
