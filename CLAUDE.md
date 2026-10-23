# AsistenteIA — Convenciones del proyecto

## Stack tecnológico
- **Backend:** FastAPI 0.115+ (Python 3.11), SQLAlchemy + Alembic, LangChain 0.3+
- **Frontend:** React 18 + TypeScript, Tailwind CSS + Headless UI, Axios + React Query
- **Base de datos:** PostgreSQL 15 con extensión pgvector (Supabase)
- **LLM:** Gemini vía API externa; modelo configurable con `GEMINI_MODEL` (por defecto `gemini-3.5-flash-lite`; `gemini-2.5-flash` ya no está disponible para cuentas nuevas)
- **Embeddings:** HuggingFace `paraphrase-multilingual-MiniLM-L12-v2` (local, vector(384))

## Arquitectura (Layered Architecture + Repository Pattern)

El backend tiene 4 capas estrictas. No mezclar responsabilidades entre capas:

1. **API Layer** (`app/api/v1/endpoints/`): routers FastAPI + schemas Pydantic. Solo recibe, valida y responde. No contiene lógica de negocio ni acceso a datos directo.
2. **Service Layer** (`app/services/`): lógica de negocio. Servicios principales: `RAGService`, `SubjectService`, `ConversationService`, `AuthService`. Un service puede llamar a otros services y a repositories, nunca accede directamente a modelos SQLAlchemy.
3. **Repository Layer** (`app/repositories/`): acceso a datos (SQLAlchemy + consultas pgvector). Un repository no llama a services ni a otros repositories.
4. **Models** (`app/models/`): entidades SQLAlchemy. **Schemas** (`app/schemas/`): Pydantic (request/response).

## Modelo de datos (entidades principales)
- `User` (id, name, email UK, password_hash, role: teacher|student)
- `Subject` (id, name, description, teacher_id FK)
- `Document` (id, subject_id FK CASCADE, filename) — metadatos del archivo
- `DocumentChunk` (id, document_id FK CASCADE, content, embedding vector(384)) — fragmento indexado para RAG
- `Conversation` (id, student_id FK, subject_id FK)
- `Message` (id, conversation_id FK, role: user|assistant, content)
- `MessageSource` (id, message_id FK CASCADE, document_chunk_id FK) — fuentes citadas por respuesta

No hay tabla de inscripción: cualquier estudiante autenticado accede a cualquier asignatura.

## API REST (contrato)
- Autenticación: JWT (Bearer token). Endpoints `/auth/register` y `/auth/login`.
- Endpoints protegidos: todos los demás requieren `Authorization: Bearer <token>`.
- Validación: Pydantic schemas en todos los endpoints.
- Respuesta del chat (`POST /chat`): devuelve `sources` como **array** de fragmentos citados, no una sola fuente.

## Índice vectorial
- Usar **hnsw** (no ivfflat) sobre `document_chunks.embedding` con operador de distancia coseno. hnsw rinde mejor con pocos datos.

## Convenciones de código
- **Python:** snake_case para funciones y variables, PascalCase para clases.
- **TypeScript/React:** camelCase para funciones y variables, PascalCase para componentes.
- Archivos de servicio: `rag_service.py`, `subject_service.py`, etc.
- Archivos de repository: `document_chunk_repository.py`, etc.
- Un archivo por router en `api/v1/endpoints/`.

## Tests
- Backend: Pytest. Tests unitarios del Service Layer con mocks; tests de integración de endpoints.
- Frontend: Vitest + React Testing Library.
- E2E: Playwright (flujo completo docente sube → estudiante pregunta → respuesta citada).

## Reglas para el asistente de IA
- No crear archivos fuera de la estructura definida en `backend/app/` y `frontend/src/`.
- No mezclar capas: un router nunca importa un model directamente; un repository nunca importa un service.
- No hardcodear claves de API ni credenciales; usar variables de entorno (`app/core/config.py`).
- No cambiar el tipo de índice vectorial sin justificación explícita.
- Las respuestas del chat siempre deben incluir las fuentes como array, incluso si es una sola.
