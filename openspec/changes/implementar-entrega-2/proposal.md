# Proposal

## Why

El proyecto AsistenteIA completó la Entrega 1 (documentación técnica) y necesita pasar de cero código a un MVP funcional para la Entrega 2 del proyecto final del máster AI4Devs. La fecha de entrega es el 23 de octubre de 2026. Sin código implementado, no hay producto verificable ni flujo operativo demostrable.

## What Changes

- Crear la estructura completa del proyecto (monorepo con `backend/` y `frontend/`)
- Configurar entorno de desarrollo local con Docker (PostgreSQL 15 + pgvector)
- Implementar backend FastAPI con arquitectura en 4 capas (API → Service → Repository → Models)
- Implementar sistema de autenticación con JWT y roles (teacher/student)
- Implementar CRUD de asignaturas y carga de documentos con procesamiento automático (chunking + embeddings HuggingFace)
- Implementar pipeline RAG completo: búsqueda vectorial pgvector → contexto → Gemini 2.5 Flash → respuesta con fuentes citadas
- Implementar gestión de conversaciones con historial y borrado GDPR
- Implementar frontend React 18 + TypeScript + Tailwind con vistas para docente y estudiante
- Crear migraciones Alembic para todo el modelo de datos (User, Subject, Document, DocumentChunk, Conversation, Message, MessageSource) con índice hnsw
- Actualizar README.md con instrucciones de instalación y credenciales de prueba

## Capabilities

### New Capabilities

- `user-auth`: Registro y autenticación de usuarios con JWT. Roles diferenciados (teacher/student) que determinan el acceso a funcionalidades.
- `subject-management`: Gestión de asignaturas por docentes y carga de documentos con procesamiento automático (chunking de texto + generación de embeddings) para alimentar la base de conocimiento RAG.
- `rag-chat`: Pipeline RAG completo — el estudiante pregunta sobre una asignatura, el sistema busca fragmentos relevantes por similitud vectorial, construye un prompt con contexto y genera una respuesta citando las fuentes documentales.
- `conversation-history`: Almacenamiento del historial de conversaciones por estudiante/asignatura, con capacidad de eliminación por parte del estudiante (derecho al olvido GDPR).

### Modified Capabilities

(ninguna — proyecto greenfield, no hay capabilities existentes)

## Impact

- **Código nuevo**: se crea toda la estructura `backend/` (FastAPI, SQLAlchemy, Alembic, LangChain) y `frontend/` (React, TypeScript, Tailwind, Axios, React Query)
- **Infraestructura local**: `docker-compose.yml` con PostgreSQL 15 + pgvector
- **Dependencias externas**: Gemini 2.5 Flash API (requiere API key), modelo HuggingFace `paraphrase-multilingual-MiniLM-L12-v2` (descarga local)
- **API REST**: todos los endpoints definidos en la Entrega 1 (auth, subjects, documents, chat, conversations)
- **Base de datos**: 7 tablas nuevas con extensión pgvector e índice hnsw sobre embeddings
