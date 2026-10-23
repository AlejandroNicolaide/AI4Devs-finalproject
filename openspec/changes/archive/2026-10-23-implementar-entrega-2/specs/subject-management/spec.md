# Spec Delta

## Purpose

Gestión de asignaturas por docentes y carga de documentos con procesamiento automático (chunking + embeddings) para alimentar la base de conocimiento RAG del sistema.

## ADDED Requirements

### Requirement: Create subject
Un docente autenticado SHALL poder crear una asignatura proporcionando name y description. La asignatura queda vinculada al docente que la creó (teacher_id).

#### Scenario: Creación exitosa
- **WHEN** un docente autenticado envía POST /subjects con name y description
- **THEN** el sistema crea la asignatura y responde con id, name, description y teacher_id

#### Scenario: Estudiante intenta crear asignatura
- **WHEN** un usuario con role student envía POST /subjects
- **THEN** el sistema responde 403

### Requirement: List subjects
Cualquier usuario autenticado SHALL poder listar las asignaturas disponibles en el sistema.

#### Scenario: Listar asignaturas
- **WHEN** un usuario autenticado envía GET /subjects
- **THEN** el sistema responde con un array de asignaturas (id, name, description, teacher_id)

### Requirement: Upload document
Un docente SHALL poder subir un documento (archivo PDF o texto) a una asignatura de la que es titular. El sistema MUST procesar el documento automáticamente: extraer texto, dividirlo en fragmentos (chunks) y generar embeddings con el modelo HuggingFace paraphrase-multilingual-MiniLM-L12-v2 (vector(384)).

#### Scenario: Carga y procesamiento exitoso
- **WHEN** un docente titular de la asignatura envía POST /subjects/{subject_id}/documents con un archivo PDF o texto
- **THEN** el sistema extrae el texto, genera los chunks con embeddings, los almacena en document_chunks, y responde 201 con id, filename y chunks_created

#### Scenario: Docente no titular intenta subir
- **WHEN** un docente que no es titular de la asignatura intenta subir un documento
- **THEN** el sistema responde 403

#### Scenario: Formato de archivo no soportado
- **WHEN** un docente sube un archivo con formato no soportado (ni PDF ni texto)
- **THEN** el sistema responde con un error indicando los formatos aceptados

### Requirement: List documents
Un docente titular SHALL poder ver los documentos cargados en su asignatura.

#### Scenario: Listar documentos de una asignatura
- **WHEN** un docente titular envía GET /subjects/{subject_id}/documents
- **THEN** el sistema responde con un array de documentos (id, filename, created_at)

### Requirement: Cascade delete
Al eliminar una asignatura, el sistema MUST eliminar en cascada todos los documentos, chunks y sus embeddings asociados.

#### Scenario: Eliminación en cascada
- **WHEN** se elimina una asignatura
- **THEN** se eliminan todos sus documentos y document_chunks asociados automáticamente
