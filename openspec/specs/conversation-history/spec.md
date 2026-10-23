# conversation-history Specification

## Purpose

Almacenamiento y consulta del historial de conversaciones por estudiante y asignatura, con capacidad de eliminación para cumplir el derecho al olvido (GDPR).

## Requirements

### Requirement: List conversations
Un estudiante autenticado SHALL poder listar sus propias conversaciones, opcionalmente filtradas por asignatura.

#### Scenario: Listar conversaciones propias
- **WHEN** un estudiante envía GET /conversations
- **THEN** el sistema responde con un array de conversaciones propias (id, subject_id, created_at)

#### Scenario: Filtrar por asignatura
- **WHEN** un estudiante envía GET /conversations?subject_id={id}
- **THEN** el sistema responde solo con las conversaciones de esa asignatura

### Requirement: Get conversation messages
Un estudiante autenticado SHALL poder consultar los mensajes de una conversación propia.

#### Scenario: Consultar mensajes
- **WHEN** un estudiante envía GET /conversations/{conversation_id}/messages
- **THEN** el sistema responde con los mensajes ordenados cronológicamente (id, role, content, created_at)

#### Scenario: Consultar conversación ajena
- **WHEN** un estudiante intenta consultar los mensajes de una conversación de otro usuario
- **THEN** el sistema responde 403

### Requirement: Delete conversation (GDPR)
Un estudiante SHALL poder eliminar una conversación propia y todos sus mensajes y fuentes asociadas. La eliminación MUST ser irreversible y en cascada (Conversation → Messages → MessageSources).

#### Scenario: Eliminación exitosa
- **WHEN** un estudiante envía DELETE /conversations/{conversation_id} sobre una conversación propia
- **THEN** el sistema elimina la conversación, sus mensajes y message_sources, y responde 204

#### Scenario: Eliminar conversación ajena
- **WHEN** un estudiante intenta eliminar una conversación de otro usuario
- **THEN** el sistema responde 403

#### Scenario: Conversación inexistente
- **WHEN** un estudiante envía DELETE /conversations/{conversation_id} con un id que no existe
- **THEN** el sistema responde 404
