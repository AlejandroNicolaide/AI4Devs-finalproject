> Detalla en esta sección los prompts principales utilizados durante la creación del proyecto, que justifiquen el uso de asistentes de código en todas las fases del ciclo de vida del desarrollo. Esperamos un máximo de 3 por sección, principalmente los de creación inicial o  los de corrección o adición de funcionalidades que consideres más relevantes.
Puedes añadir adicionalmente la conversación completa como link o archivo adjunto si así lo consideras


## Índice

1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Modelo de datos](#3-modelo-de-datos)
4. [Especificación de la API](#4-especificación-de-la-api)
5. [Historias de usuario](#5-historias-de-usuario)
6. [Tickets de trabajo](#6-tickets-de-trabajo)
7. [Pull requests](#7-pull-requests)

---

## 1. Descripción general del producto

**Prompt 1:**

```
En los archivos adjuntados esta la información sobre el Proyecto Final (readme.md, prompts.md y las
lecciones del máster). Ya realicé el fork y clonado en local del repo del proyecto final. Estos son
repos de ejemplo para referencia (2 completos con todos los entregables, 2 con solo la entrega 1).
La idea es darte contexto de la necesidad, no codifiques nada, quiero que me vayas consultando para
saber si entendiste correctamente y a partir de ahí vamos iterando para cumplimentar el trabajo.

Mi idea de proyecto: un agente de IA generativa diseñado para acompañar a estudiantes y tutores
durante el recorrido académico, generar interacciones de valor y ampliar las oportunidades de
aprendizaje (RAG). Debe estar disponible para varias asignaturas, permitiendo que los estudiantes
aprendan a su propio ritmo, consulten contenidos y resuelvan dudas relacionadas con sus cursos.
Cada asistente es alimentado por los docentes con la bibliografía y los contenidos de la asignatura.
Además contemplo un asistente de servicio al estudiante (matrícula, toma de ramos, titulación,
consultas académicas) y un módulo de monitoreo del aprendizaje para docentes, con integración a un
LMS tipo Moodle.
```

**Prompt 2:**

```
Quiero acotar el alcance del MVP: el foco principal va a ser el asistente académico RAG por
asignatura. La integración con Moodle queda fuera del MVP (los docentes suben material manualmente
vía la propia app). El módulo de monitoreo/analítica para docentes queda como should-have, no
obligatorio. Además quiero agregar protección de datos (GDPR) como parte del alcance.

Datos para la ficha del proyecto:
- Nombre completo: Alejandro Nicolaide
- Nombre del proyecto: AsistenteIA (descartamos "GuIA" por coincidir con un producto real existente)
- Descripción breve: un chatbot RAG diseñado para acompañar a estudiantes y tutores durante el
  recorrido académico, para generar interacciones de valor y ampliar las oportunidades de aprendizaje.
- URL del proyecto: pendiente de despliegue
- Repositorio: https://github.com/AlejandroNicolaide/AI4Devs-finalproject

Con esto, redacta el objetivo (1.1) usando un caso de uso de una institución educativa ficticia, y las
características y funcionalidades principales (1.2), incluyendo la eliminación de historial de
conversaciones como funcionalidad GDPR y dejando la analítica docente marcada como should-have.
```

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

**Prompt 1:**

```
Propón un patrón de arquitectura para el backend (FastAPI + React + Postgres/pgvector + LangChain +
Gemini). Sugiere si conviene una arquitectura por capas con Repository Pattern, cómo se comunican
frontend y backend, y justifica ventajas y déficits de la propuesta antes de escribir nada en el
README.
```

**Prompt 2:**

```
Antes de aceptar la arquitectura propuesta, revisá qué arquitectura usa realmente el repo de
referencia AI4Devs-finalproject-Example2 (README real del repo, no solo el resumen que tengo). Quiero
saber si coincide con lo que me proponés, para tomar una decisión informada y no copiar por
casualidad.
```

**Prompt 3:**

```
Confirmado el patrón (Layered Architecture + Repository Pattern + Service Layer, RAG con LangChain).
Generá el diagrama de arquitectura en formato mermaid (flowchart) mostrando frontend, capas del
backend, PostgreSQL+pgvector, y los servicios externos (Gemini, HuggingFace embeddings), y escribilo
en la sección 2.1 del readme.md junto con la justificación del patrón y sus déficits.
```

### **2.2. Descripción de componentes principales:**

**Prompt 1:**

```
A partir del diagrama de arquitectura ya definido, describe los componentes principales del sistema
(frontend, API layer, service layer -RAGService, SubjectService, ConversationService-, repository
layer, PostgreSQL+pgvector, Gemini, HuggingFace embeddings), indicando la tecnología y responsabilidad
de cada uno, para la sección 2.2 del readme.md.
```

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

**Prompt 1:**

```
Proponeme una estructura de carpetas para backend (FastAPI) y frontend (React+TS) que refleje las
capas ya definidas (api/services/repositories/models/schemas en backend; pages/components/hooks/
services en frontend). Explicá brevemente el propósito de cada carpeta principal y si obedece a algún
patrón específico.
```

### **2.4. Infraestructura y despliegue**

**Prompt 1:**

```
El proyecto todavía no está desplegado (estamos en la Entrega 1, solo documentación). Sugerime una
combinación de infraestructura simple y gestionada (sin Kubernetes/Terraform) para desplegar backend,
frontend y base de datos con pgvector, apta para un MVP académico, y documentala en la sección 2.4
como plan de despliegue (no como despliegue ya realizado), incluyendo un diagrama.
```

### **2.5. Seguridad**

**Prompt 1:**

```
Documenta las prácticas de seguridad del proyecto en la sección 2.5, incluyendo específicamente
protección de datos conforme a GDPR: minimización de datos, consentimiento explícito, derecho al
olvido (relacionado con la funcionalidad de borrado de historial ya definida en 1.2), cifrado en
tránsito y en reposo, retención de datos, gestión de secretos y validación de entrada.
```

### **2.6. Tests**

**Prompt 1:**

```
Como todavía no existe código (Entrega 1 es solo documentación), describe en la sección 2.6 la
estrategia de testing planificada para las próximas entregas: tests unitarios y de integración en
backend (Pytest), tests de componentes en frontend (Vitest + React Testing Library), y un test E2E
del flujo principal (Playwright) para la entrega final.
```

---

### 3. Modelo de Datos

**Prompt 1:**

```
A partir de las funcionalidades ya definidas (gestión de asignaturas y material por parte del
docente, consulta RAG por parte del estudiante, historial de conversación, borrado de historial por
GDPR), proponeme las entidades principales del modelo de datos (usuarios, asignaturas, documentos con
embeddings, conversaciones, mensajes), con sus relaciones.
```

**Prompt 2:**

```
Generá el diagrama del modelo de datos en formato mermaid (erDiagram) con el máximo detalle posible
(claves primarias, foráneas, tipos de dato, restricciones), y la descripción textual de cada entidad
(atributos, tipo, PK/FK, relaciones, restricciones unique/not null), para las secciones 3.1 y 3.2 del
readme.md. Tené en cuenta que la columna embedding debe soportar pgvector.
```

**Prompt 3 (corrección post-revisión):**

```
El profesor señaló tres problemas en el modelo de datos:
1. Document guarda un fragmento por fila repitiendo filename. Hay que separar en Document (filename,
   subject_id) y DocumentChunk (content, embedding, document_id).
2. Message solo puede apuntar a una fuente (source_document_id), pero una respuesta RAG se apoya en
   varios fragmentos. Hay que crear una tabla MessageSource (message_id, document_chunk_id) para
   permitir múltiples fuentes por respuesta.
3. El índice ivfflat rinde mal con pocos datos; cambiar a hnsw.
Además, las historias y tickets hablan de "estudiante inscrito en la asignatura" pero no existe esa
relación. Decisión: simplificar para el MVP, cualquier estudiante autenticado accede a cualquier
asignatura (sin tabla de inscripción).

Aplica estos 4 cambios al diagrama ER (3.1), a la descripción de entidades (3.2), y propaga la
coherencia a la API (sección 4), las historias (sección 5) y los tickets (sección 6): quitar
"inscrito", cambiar source_document singular por sources array, y actualizar el ticket de BD con las
nuevas tablas y el índice hnsw.
```

---

### 4. Especificación de la API

**Prompt 1:**

```
Definí los 3 endpoints principales de la API (máximo 3, según la plantilla) que cubran el flujo core
del producto: subida de material por parte del docente, consulta al asistente (chat RAG) por parte
del estudiante, y borrado de historial de conversación (GDPR).
```

**Prompt 2 (corrección post-revisión):**

```
El profesor señaló que tenemos JWT y password_hash pero ningún endpoint de registro ni login. Agregá
POST /auth/register y POST /auth/login en formato OpenAPI a la sección 4 de la API. Además, actualizá
el endpoint POST /chat para que devuelva un array "sources" con múltiples fragmentos citados en vez de
un solo "source_document", coherente con el nuevo modelo de datos (DocumentChunk + MessageSource).
```

**Prompt 3:**

```
Documenta esos 3 endpoints en formato OpenAPI (paths, requestBody, responses con sus schemas) para la
sección 4 del readme.md, agregando un ejemplo de petición y de respuesta en JSON para el endpoint de
chat.
```

---

### 5. Historias de Usuario

**Prompt 1:**

```
Documenta 3 historias de usuario principales del proyecto (una por cada endpoint/funcionalidad core ya
definida: carga de material, consulta RAG, borrado de historial GDPR), usando formato Gherkin (Dado/
Cuando/Entonces) para los criterios de aceptación, e indicando la priorización (MoSCoW) de cada una,
para la sección 5 del readme.md.
```

---

### 6. Tickets de Trabajo

**Prompt 1:**

```
Documenta 3 tickets de trabajo (uno de backend, uno de frontend, uno de base de datos) alineados con
la Historia de Usuario 2 (consulta al asistente RAG), con todo el detalle necesario para desarrollar
la tarea de inicio a fin: descripción, tareas técnicas, criterios de aceptación, estimación y
dependencias entre tickets, para la sección 6 del readme.md.
```

---

### 7. Pull Requests

**Prompt 1:**

```
Esta es la Entrega 1 (solo documentación, sin código). No corresponde documentar Pull Requests
todavía. Dejá la sección 7 del readme.md con una nota indicando que se completará a partir de la
Entrega 2, en lugar de inventar PRs ficticias.
```

---

### 8. Preparación para implementación (CLAUDE.md)

**Prompt 1:**

```
El profesor recomendó crear un CLAUDE.md o .cursorrules antes de programar, con las capas, la pila,
las convenciones y el contrato de la API, para que el asistente de IA no rompa la arquitectura al
implementar. Creá un CLAUDE.md en la raíz del repo con toda la información relevante del proyecto:
stack, arquitectura por capas (qué puede importar qué), modelo de datos actualizado (Document +
DocumentChunk + MessageSource), contrato de la API (auth + endpoints core), convenciones de naming,
tipo de índice vectorial (hnsw), y reglas explícitas para el asistente.
```

---

### 9. Implementación de la Entrega 2 (OpenSpec + Claude Code)

**Herramientas y modelos:** Claude Code (extensión de VS Code) con el flujo OpenSpec (`/opsx:apply` sobre el change `implementar-entrega-2`, con proposal, specs, design y 41 tareas). Backend FastAPI + SQLAlchemy + Alembic + LangChain; frontend React 18 + Vite + Tailwind v3; LLM Gemini vía `langchain-google-genai`; embeddings HuggingFace locales. CLAUDE.md acotó las capas durante toda la implementación.

**Prompt 1 (arranque de la implementación):**

```
/opsx:apply arranquemos con la implementacion
```

Resultado: el asistente leyó proposal, specs y design, y fue ejecutando las tareas en orden (entorno Docker, modelos y migraciones, auth, subjects/documents, RAG, conversaciones, frontend), marcando cada checkbox tras verificarla (curl, psql y navegador).

**Prompt 2 (bloqueo con el modelo de Gemini):**

```
ya cargue en env la api key procede
```

Resultado: `/chat` devolvía 503. El asistente diagnosticó que la key era válida pero `gemini-2.5-flash` ya no está disponible para cuentas nuevas, y que `gemini-3.8-flash` daba 503/504 por saturación. Hizo el modelo configurable (`GEMINI_MODEL`) y añadió timeout y reintentos acotados.

**Prompt 3 (elección del modelo alternativo):**

```
recomendame otro modelo de gemini para probar
si probemos en ese orden
```

Resultado: se listaron los modelos disponibles para la key y se probaron en orden `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-3.5-flash`, `gemini-flash-lite-latest`. El primero respondió en ~1.5 s con el prompt RAG real y quedó como modelo por defecto.

**Ajustes y decisiones humanas durante la implementación:**

- **Puerto de PostgreSQL:** el 5432 y el 5433 estaban ocupados por contenedores de otro proyecto; se usó el 5434 (configurable con `POSTGRES_PORT`) sin tocar los otros contenedores.
- **Modelo de LLM:** el usuario eligió probar otro modelo en lugar de mantener o fijar uno; el cambio de `gemini-2.5-flash` a `gemini-3.5-flash-lite` se documentó en el README.
- **React 18:** la plantilla de Vite traía React 19; se fijó React 18 por CLAUDE.md. Tailwind v3 (no v4) por coherencia con `tailwind.config.js` del plan.
- **Desviaciones menores respecto a las tareas:** se añadió `GET /subjects/{id}` (lo necesita la vista de detalle), `ConversationService` (el router no puede llamar a repositories), `ON DELETE CASCADE` en `messages` y `message_sources` (necesario para el borrado GDPR) y el driver `postgresql+psycopg2://` (SQLAlchemy 2.1 usa psycopg v3 por defecto).
- **Verificación:** sin tests automatizados (no exigidos en la Entrega 2); el flujo completo docente → estudiante → respuesta con fuentes → historial → borrado se validó manualmente en el navegador.
