## MODIFIED Requirements

### Requirement: Answer question with RAG
El sistema SHALL recibir una pregunta del estudiante sobre una asignatura (POST /chat con subject_id y message), buscar los fragmentos más relevantes por similitud vectorial (coseno, índice hnsw), construir un prompt con el contexto recuperado, y generar una respuesta usando el modelo de Gemini configurado por entorno (`GEMINI_MODEL`).

#### Scenario: Pregunta con material disponible
- **WHEN** un estudiante envía POST /chat con subject_id de una asignatura que tiene material indexado y un message con su pregunta
- **THEN** el sistema responde con conversation_id, answer (texto generado) y sources (array de fragmentos citados con chunk_id, document_id, filename y fragment)

#### Scenario: Primera pregunta crea conversación
- **WHEN** un estudiante envía POST /chat sin conversation_id
- **THEN** el sistema crea una nueva conversación y la devuelve en conversation_id

#### Scenario: Pregunta en conversación existente
- **WHEN** un estudiante envía POST /chat con un conversation_id válido
- **THEN** el sistema agrega el mensaje a la conversación existente

## ADDED Requirements

### Requirement: Conversation history in answers
Cuando la pregunta pertenece a una conversación existente, el sistema MUST incluir en el contexto enviado al modelo los mensajes más recientes de esa conversación, de modo que la respuesta pueda apoyarse en lo ya conversado. El historial incluido SHALL estar acotado a un máximo de mensajes y SHALL ser solo el de esa conversación.

#### Scenario: Pregunta de seguimiento
- **WHEN** un estudiante envía POST /chat con un conversation_id que ya tiene mensajes y una pregunta que depende de la respuesta anterior
- **THEN** el modelo recibe esos mensajes previos junto con la nueva pregunta y los fragmentos recuperados

#### Scenario: Primera pregunta sin historial
- **WHEN** un estudiante envía POST /chat sin conversation_id
- **THEN** el modelo recibe solo la pregunta y los fragmentos recuperados

#### Scenario: Historial acotado
- **WHEN** la conversación supera el máximo de mensajes de historial permitido
- **THEN** solo se incluyen los mensajes más recientes hasta ese máximo

### Requirement: Minimum similarity threshold
El sistema SHALL admitir un umbral de similitud mínimo configurable (`SIMILARITY_THRESHOLD`). Si está definido y ningún fragmento recuperado lo supera, el sistema MUST responder con un mensaje controlado indicando que no encontró información relevante en el material, sin invocar al modelo de lenguaje y con sources como array vacío. Si no está definido, el comportamiento es el anterior (se usan los fragmentos recuperados).

#### Scenario: Ningún fragmento supera el umbral
- **WHEN** una asignatura tiene material indexado pero ningún fragmento supera el umbral para la pregunta realizada
- **THEN** el sistema responde con un answer que informa que no hay información relevante en el material, sources vacío, y no llama al modelo de lenguaje

#### Scenario: Algún fragmento supera el umbral
- **WHEN** al menos un fragmento supera el umbral
- **THEN** el prompt incluye solo los fragmentos que lo superan y sources los lista

#### Scenario: Umbral no configurado
- **WHEN** `SIMILARITY_THRESHOLD` no está definido
- **THEN** el sistema usa los fragmentos recuperados sin filtrar por similitud
