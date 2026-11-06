-- AsistenteIA: creación completa de la base de datos (equivalente a las migraciones de Alembic).
-- Idempotente: se puede ejecutar varias veces. Deja alembic_version en la revisión a1hnsw0001,
-- así que `alembic upgrade head` posterior no hace nada.
--
-- Uso:
--   psql "postgresql://USUARIO:CLAVE@HOST:PUERTO/asistenteia" -f backend/scripts/init_db.sql
-- (la base `asistenteia` debe existir; con la imagen pgvector/pgvector:pg15 se crea con POSTGRES_DB)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    email         VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT ck_users_role CHECK (role IN ('teacher', 'student'))
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE TABLE IF NOT EXISTS subjects (
    id          UUID PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    teacher_id  UUID NOT NULL REFERENCES users (id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_subjects_teacher_id ON subjects (teacher_id);

CREATE TABLE IF NOT EXISTS conversations (
    id         UUID PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES users (id),
    subject_id UUID NOT NULL REFERENCES subjects (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_conversations_student_id ON conversations (student_id);
CREATE INDEX IF NOT EXISTS ix_conversations_subject_id ON conversations (subject_id);

CREATE TABLE IF NOT EXISTS documents (
    id         UUID PRIMARY KEY,
    subject_id UUID NOT NULL REFERENCES subjects (id) ON DELETE CASCADE,
    filename   VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_documents_subject_id ON documents (subject_id);

CREATE TABLE IF NOT EXISTS document_chunks (
    id          UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    embedding   VECTOR(384) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_document_chunks_document_id ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw
    ON document_chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations (id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL,
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_messages_role CHECK (role IN ('user', 'assistant'))
);
CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id);

CREATE TABLE IF NOT EXISTS message_sources (
    id                UUID PRIMARY KEY,
    message_id        UUID NOT NULL REFERENCES messages (id) ON DELETE CASCADE,
    document_chunk_id UUID NOT NULL REFERENCES document_chunks (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_message_sources_document_chunk_id ON message_sources (document_chunk_id);
CREATE INDEX IF NOT EXISTS ix_message_sources_message_id ON message_sources (message_id);

-- Marca de Alembic: la base queda alineada con `alembic upgrade head`.
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);
DELETE FROM alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('a1hnsw0001');
