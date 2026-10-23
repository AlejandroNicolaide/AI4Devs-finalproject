## Índice

0. [Ficha del proyecto](#0-ficha-del-proyecto)
1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Modelo de datos](#3-modelo-de-datos)
4. [Especificación de la API](#4-especificación-de-la-api)
5. [Historias de usuario](#5-historias-de-usuario)
6. [Tickets de trabajo](#6-tickets-de-trabajo)
7. [Pull requests](#7-pull-requests)

---

## 0. Ficha del proyecto

### **0.1. Tu nombre completo:**

Alejandro Nicolaide

### **0.2. Nombre del proyecto:**

AsistenteIA

### **0.3. Descripción breve del proyecto:**

AsistenteIA es un chatbot basado en RAG (Retrieval-Augmented Generation) que acompaña a estudiantes y tutores durante el recorrido académico, respondiendo dudas sobre el contenido de cada asignatura a partir del material cargado por los docentes.

### **0.4. URL del proyecto:**

Pendiente de despliegue.

> Puede ser pública o privada, en cuyo caso deberás compartir los accesos de manera segura. Puedes enviarlos a [alvaro@lidr.co](mailto:alvaro@lidr.co) usando algún servicio como [onetimesecret](https://onetimesecret.com/).

### 0.5. URL o archivo comprimido del repositorio

https://github.com/AlejandroNicolaide/AI4Devs-finalproject

> Puedes tenerlo alojado en público o en privado, en cuyo caso deberás compartir los accesos de manera segura. Puedes enviarlos a [alvaro@lidr.co](mailto:alvaro@lidr.co) usando algún servicio como [onetimesecret](https://onetimesecret.com/). También puedes compartir por correo un archivo zip con el contenido


---

## 1. Descripción general del producto

> Describe en detalle los siguientes aspectos del producto:

### **1.1. Objetivo:**

AsistenteIA busca resolver un problema frecuente en instituciones educativas (caso de uso de referencia: Instituto Delta, institución ficticia): los estudiantes tienen dudas puntuales sobre el contenido de sus asignaturas fuera del horario de clase, y los docentes no dan abasto para responder consultas repetitivas de forma individual.

AsistenteIA permite que cada docente cargue la bibliografía y el material de su asignatura, y que los estudiantes consulten esas dudas en cualquier momento, recibiendo respuestas ancladas al material real del curso (no respuestas genéricas), con la fuente citada para poder verificar la información. Esto libera tiempo docente para consultas de mayor valor y da a los estudiantes autonomía para aprender a su propio ritmo.

### **1.2. Características y funcionalidades principales:**

- **Gestión de asignaturas y carga de material (docente):** alta de asignatura, subida de documentos (PDF/texto) que alimentan la base de conocimiento de esa asignatura.
- **Consulta con RAG (estudiante):** el estudiante selecciona una asignatura y pregunta en lenguaje natural; recibe una respuesta generada a partir del material de esa asignatura, con referencia al documento/fragmento de origen.
- **Historial de conversación** por estudiante y asignatura.
- **Eliminación de historial de conversaciones (GDPR / derecho al olvido):** el estudiante puede borrar sus datos conversacionales almacenados.
- *(should-have, no incluido en el alcance obligatorio del MVP)* Panel de analítica para docentes con preguntas frecuentes y temas de mayor dificultad.
- *(nice-to-have, opcional)* Control de alucinaciones: umbral de similitud mínimo en el pipeline RAG; si ningún fragmento recuperado supera ese umbral, el asistente responde que no encontró información relevante en el material, en lugar de generar una respuesta sin respaldo.

### **1.3. Diseño y experiencia de usuario:**

La interfaz es una SPA (React + Tailwind) con dos perfiles:

- **Docente:** inicia sesión, crea asignaturas desde el listado ("Crear asignatura"), entra al detalle de la suya y sube material (PDF o TXT). Al terminar la subida ve cuántos fragmentos se generaron y la lista de documentos cargados.
- **Estudiante:** ve todas las asignaturas, entra a una y pulsa "Preguntar al asistente". En el chat escribe su pregunta (indicador "escribiendo…" mientras responde) y recibe la respuesta con un bloque **Fuentes**: chips con el nombre del documento y el fragmento citado, que se expande al pulsar. Desde **Historial** puede continuar una conversación anterior o eliminarla (con confirmación, derecho al olvido).

Flujo verificado de extremo a extremo en el navegador: registro de docente → crear asignatura → subir PDF → registro de estudiante → pregunta → respuesta con fuentes → historial → eliminar conversación.

### **1.4. Instrucciones de instalación:**

**Requisitos:** Git, Docker Desktop, Python 3.11+ (probado con 3.13), Node.js 20+ y una API key de Gemini (gratuita, en [Google AI Studio](https://aistudio.google.com/)).

```bash
# 1. Clonar
git clone <url-del-repositorio> && cd AI4Devs-finalproject

# 2. Base de datos (PostgreSQL 15 + pgvector). Puerto del host: 5434 por defecto
docker compose up -d
#    Si 5434 está ocupado: POSTGRES_PORT=5435 docker compose up -d (y ajusta DATABASE_URL)

# 3. Backend
cd backend
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # y edita SECRET_KEY y GEMINI_API_KEY
alembic upgrade head             # crea las tablas, la extensión vector y el índice hnsw
uvicorn app.main:app --reload    # http://localhost:8000  (docs en /docs)

# 4. Frontend (otra terminal)
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

**Variables de entorno (`backend/.env`):** `DATABASE_URL` (por defecto `postgresql+psycopg2://postgres:postgres@localhost:5434/asistenteia`), `SECRET_KEY`, `GEMINI_API_KEY` y `GEMINI_MODEL` (por defecto `gemini-3.5-flash-lite`; `gemini-2.5-flash` ya no está disponible para cuentas nuevas de Google AI Studio).

**Notas:**
- La primera subida de un documento descarga el modelo de embeddings de HuggingFace (~120 MB, puede tardar unos minutos); después queda en caché.
- Sin `GEMINI_API_KEY` el resto de la aplicación funciona, pero `/chat` responde 503 en asignaturas con material.
- No hay usuarios seed: crea un docente y un estudiante desde `/register`.

**Prueba rápida:** regístrate como Docente → crea una asignatura → sube un PDF con texto → cierra sesión → regístrate como Estudiante → entra a la asignatura y pregunta sobre el contenido del PDF.

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

```mermaid
flowchart TB
    subgraph Client["Frontend"]
        UI["React 18 + TypeScript\nTailwind + Headless UI\nAxios + React Query"]
    end

    subgraph API["Backend - FastAPI"]
        Router["API Layer\nRouters + Pydantic schemas"]
        Service["Service Layer\nRAGService · SubjectService · ConversationService"]
        Repo["Repository Layer\nAbstracción de acceso a datos"]
    end

    subgraph Data["Persistencia"]
        PG[("PostgreSQL 15\nAsignaturas, usuarios, conversaciones")]
        VEC[("pgvector\nEmbeddings de documentos")]
    end

    subgraph External["Servicios externos"]
        LLM["Gemini (3.5 Flash-Lite)\n(generación de respuestas)"]
        EMB["HuggingFace\nparaphrase-multilingual-MiniLM-L12-v2\n(embeddings, local)"]
    end

    UI -- "REST / JSON (OpenAPI)" --> Router
    Router --> Service
    Service --> Repo
    Repo --> PG
    Repo --> VEC
    Service -- "prompt + contexto recuperado" --> LLM
    Service -- "generación de embeddings" --> EMB
```

**Patrón:** Arquitectura en capas (Layered Architecture) con **Repository Pattern** y **Service Layer**, sobre un pipeline RAG (LangChain) para la generación de respuestas.

**Por qué esta arquitectura:**
- Separa responsabilidades: la capa API no conoce lógica de negocio, el Service Layer no conoce detalles de persistencia, y el Repository Layer aísla el acceso a PostgreSQL/pgvector.
- Permite cambiar el proveedor de LLM, el modelo de embeddings o el vector store sin modificar routers ni lógica de negocio — relevante en un proyecto de IA donde estas piezas evolucionan rápido.
- Es el mismo patrón usado en los proyectos de referencia (Example1 y Example2) porque es el enfoque estándar para este tipo de sistema; la decisión se adoptó por ser la solución correcta al problema, no por copia.

**Déficits/sacrificios:**
- Para un MVP de este tamaño, las capas añaden código de "paso" (boilerplate) que en un prototipo más pequeño no sería estrictamente necesario.
- Mayor curva de entendimiento inicial del proyecto frente a un monolito simple sin separación de capas.

### **2.2. Descripción de componentes principales:**

- **Frontend (React 18 + TypeScript):** interfaz para docentes (gestión de asignaturas y material) y estudiantes (chat por asignatura). Se comunica con el backend vía REST usando Axios, con React Query para cacheo y estado de las peticiones.
- **API Layer (FastAPI):** expone los endpoints REST, documentados automáticamente vía OpenAPI/Swagger. Valida entrada/salida con esquemas Pydantic. No contiene lógica de negocio.
- **Service Layer:**
  - `RAGService`: orquesta el pipeline RAG (chunking del material subido, generación de embeddings, recuperación de fragmentos relevantes por similitud, construcción del prompt con contexto, llamada al LLM). Opcionalmente puede incorporar un umbral de similitud mínimo configurable para evitar respuestas sin respaldo documental (control de alucinaciones).
  - `SubjectService`: gestión de asignaturas y material asociado.
  - `ConversationService`: historial de conversaciones por estudiante/asignatura y borrado de historial (GDPR).
- **Repository Layer:** abstrae el acceso a datos (SQLAlchemy sobre PostgreSQL para entidades relacionales, consultas de similitud vectorial sobre pgvector).
- **PostgreSQL 15 + pgvector:** base de datos relacional única, con la extensión pgvector para almacenar y consultar embeddings por similitud — evita mantener una base de datos vectorial separada.
- **Gemini (`gemini-3.5-flash-lite`, configurable con `GEMINI_MODEL`):** modelo de lenguaje externo, usado en la etapa de generación de la respuesta final a partir del contexto recuperado.
- **HuggingFace `paraphrase-multilingual-MiniLM-L12-v2`:** modelo de embeddings multilingüe, ejecutado localmente (sin costo por llamada), usado tanto para indexar el material de las asignaturas como para vectorizar las preguntas de los estudiantes.

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

El proyecto está organizado como un **monorepo** con dos aplicaciones independientes (`backend` y `frontend`), cada una desplegable por separado, comunicadas vía REST.

```
backend/
  app/
    api/v1/endpoints/   # Routers FastAPI (auth, subjects, chat, documents)
    services/           # Lógica de negocio: rag_service, subject_service, conversation_service
    repositories/        # Acceso a datos (SQLAlchemy + consultas pgvector)
    models/              # Entidades SQLAlchemy (Subject, Document, DocumentChunk, Conversation, Message, MessageSource)
    schemas/             # Esquemas Pydantic (request/response)
    core/                # Configuración, variables de entorno, secretos
    main.py              # Punto de entrada de la app FastAPI
frontend/
  src/
    pages/                # Vistas (login, listado de asignaturas, chat, panel docente)
    components/           # Componentes de UI reutilizables
    hooks/                 # Hooks propios (React Query, estado de chat)
    services/              # Llamadas a la API (Axios)
```

La estructura del `backend` refleja directamente las capas descritas en 2.1/2.2 (API → Services → Repositories → Models), de modo que cada carpeta corresponde a una responsabilidad concreta del patrón Layered Architecture + Repository Pattern. El `frontend` sigue una organización estándar por tipo de artefacto (páginas, componentes, hooks, servicios), habitual en proyectos React con TypeScript.

### **2.4. Infraestructura y despliegue**

> Nota: a fecha de esta entrega (Entrega 1 - documentación), el proyecto aún no está desplegado. Esta sección describe el plan de infraestructura y despliegue previsto para las siguientes entregas.

```mermaid
flowchart LR
    Dev["Repositorio GitHub\n(main / ramas de entrega)"] -- "push / PR" --> CI["GitHub Actions\n(build + tests)"]
    CI -- "deploy automático" --> FE["Vercel\nFrontend (React)"]
    CI -- "deploy automático" --> BE["Render / Railway\nBackend (FastAPI, Docker)"]
    BE --> DB[("Supabase Postgres\ncon extensión pgvector")]
    BE --> LLMEXT["Gemini API"]
    Usuario["Usuario (docente/estudiante)"] --> FE
    FE --> BE
```

**Componentes de infraestructura:**
- **Frontend:** desplegado en **Vercel**, con integración directa al repositorio (deploy automático en cada push a la rama principal).
- **Backend:** desplegado en **Render** o **Railway** como contenedor (Docker), a partir de la carpeta `backend/`.
- **Base de datos:** **Supabase Postgres**, que incluye la extensión `pgvector` habilitada por defecto, evitando gestionar infraestructura de base de datos propia.
- **CI/CD:** **GitHub Actions**, con un workflow simple que ejecuta build y tests en cada push/PR antes de habilitar el despliegue automático.
- **Secretos:** claves de API (Gemini) y credenciales de base de datos gestionadas como variables de entorno en cada plataforma (Vercel/Render), nunca versionadas en el repositorio.

Esta combinación se eligió por ser gestionada (sin necesidad de administrar servidores, Kubernetes o Terraform), adecuada al alcance de un MVP académico, con despliegue automático desde el propio repositorio.

### **2.5. Seguridad**

- **Autenticación y roles:** acceso diferenciado por rol (docente/estudiante) mediante JWT; un docente solo gestiona el material de sus propias asignaturas, un estudiante solo accede a su propio historial.
- **Protección de datos (GDPR):**
  - Minimización de datos: solo se almacena lo estrictamente necesario para el funcionamiento (identificador de usuario, mensajes de la conversación, asignatura asociada), sin datos sensibles adicionales.
  - Consentimiento explícito: el usuario acepta el tratamiento de sus datos conversacionales en el primer login (aceptación de política de privacidad).
  - Derecho al olvido: el estudiante puede eliminar su historial de conversaciones desde la propia aplicación (funcionalidad ya listada en 1.2).
  - Cifrado en tránsito: comunicación exclusivamente vía HTTPS entre frontend, backend y base de datos.
  - Cifrado en reposo: gestionado por el proveedor de base de datos (Supabase Postgres).
  - Retención: los datos conversacionales se conservan solo mientras la cuenta esté activa o hasta que el usuario solicite su borrado.
- **Gestión de secretos:** claves de API (Gemini) y credenciales de base de datos como variables de entorno, nunca en el repositorio.
- **Validación de entrada:** esquemas Pydantic en cada endpoint, previniendo inyección y payloads malformados antes de llegar a la capa de servicio.

### **2.6. Tests**

> Nota: a fecha de esta entrega (Entrega 1 - documentación) aún no existe código; esta sección describe la estrategia de testing planificada para las siguientes entregas.

- **Backend (Pytest):** tests unitarios sobre el Service Layer (ej. `RAGService` con mocks del LLM y del retriever), y tests de integración sobre los endpoints principales (`/subjects`, `/chat`, `/documents`) usando una base de datos de test.
- **Frontend (Vitest + React Testing Library):** tests unitarios de componentes clave (formulario de carga de material, componente de chat).
- **E2E (Playwright, planificado para la entrega final):** al menos un flujo completo — docente sube material → estudiante pregunta → recibe respuesta con fuente citada.
- Cobertura: no obligatoria en esta entrega; se retoma explícitamente en la Entrega 3 (final), según la guía del máster.

---

## 3. Modelo de Datos

### **3.1. Diagrama del modelo de datos:**

```mermaid
erDiagram
    USER ||--o{ SUBJECT : "imparte (como docente)"
    USER ||--o{ CONVERSATION : "inicia (como estudiante)"
    SUBJECT ||--o{ DOCUMENT : "contiene"
    DOCUMENT ||--o{ DOCUMENT_CHUNK : "se fragmenta en"
    SUBJECT ||--o{ CONVERSATION : "se consulta en"
    CONVERSATION ||--o{ MESSAGE : "contiene"
    MESSAGE ||--o{ MESSAGE_SOURCE : "cita"
    DOCUMENT_CHUNK ||--o{ MESSAGE_SOURCE : "es citado en"

    USER {
        uuid id PK
        string name
        string email UK
        string password_hash
        string role "teacher | student"
        datetime created_at
    }

    SUBJECT {
        uuid id PK
        string name
        string description
        uuid teacher_id FK
        datetime created_at
    }

    DOCUMENT {
        uuid id PK
        uuid subject_id FK
        string filename
        datetime created_at
    }

    DOCUMENT_CHUNK {
        uuid id PK
        uuid document_id FK
        text content
        vector embedding "pgvector, vector(384)"
        datetime created_at
    }

    CONVERSATION {
        uuid id PK
        uuid student_id FK
        uuid subject_id FK
        datetime created_at
    }

    MESSAGE {
        uuid id PK
        uuid conversation_id FK
        string role "user | assistant"
        text content
        datetime created_at
    }

    MESSAGE_SOURCE {
        uuid id PK
        uuid message_id FK
        uuid document_chunk_id FK
    }
```

### **3.2. Descripción de entidades principales:**

- **User**: representa tanto a docentes como estudiantes. Cualquier estudiante autenticado puede consultar cualquier asignatura (sin tabla de inscripción, simplificación para el MVP).
  - `id` (PK, uuid), `name` (string, not null), `email` (string, unique, not null), `password_hash` (string, not null), `role` (enum: `teacher` | `student`, not null), `created_at` (datetime).
  - Relación 1:N con `Subject` (un docente imparte varias asignaturas, vía `teacher_id`).
  - Relación 1:N con `Conversation` (un estudiante inicia varias conversaciones, vía `student_id`).

- **Subject** (asignatura): creada y gestionada por un docente.
  - `id` (PK, uuid), `name` (string, not null), `description` (string), `teacher_id` (FK → User.id, not null), `created_at` (datetime).
  - Relación 1:N con `Document` (una asignatura tiene varios documentos de material).
  - Relación 1:N con `Conversation` (una asignatura es consultada en varias conversaciones).

- **Document**: archivo de material subido por el docente (metadatos del archivo original).
  - `id` (PK, uuid), `subject_id` (FK → Subject.id, not null, `ON DELETE CASCADE`), `filename` (string, not null), `created_at` (datetime).
  - Relación 1:N con `DocumentChunk` (un documento se divide en múltiples fragmentos para RAG).

- **DocumentChunk**: fragmento individual de un documento, con su embedding para búsqueda por similitud.
  - `id` (PK, uuid), `document_id` (FK → Document.id, not null, `ON DELETE CASCADE`), `content` (text, not null — fragmento de texto extraído del documento original), `embedding` (vector(384), generado con HuggingFace `paraphrase-multilingual-MiniLM-L12-v2`, indexado con `hnsw` sobre pgvector), `created_at` (datetime).

- **Conversation**: sesión de consulta de un estudiante sobre una asignatura concreta.
  - `id` (PK, uuid), `student_id` (FK → User.id, not null), `subject_id` (FK → Subject.id, not null), `created_at` (datetime).
  - Relación 1:N con `Message`.

- **Message**: cada turno dentro de una conversación (pregunta del estudiante o respuesta del asistente).
  - `id` (PK, uuid), `conversation_id` (FK → Conversation.id, not null), `role` (enum: `user` | `assistant`, not null), `content` (text, not null), `created_at` (datetime).
  - Relación 1:N con `MessageSource` (un mensaje del asistente puede citar múltiples fragmentos como fuente).

- **MessageSource**: relación entre un mensaje del asistente y los fragmentos que sirvieron de fuente para la respuesta (trazabilidad RAG).
  - `id` (PK, uuid), `message_id` (FK → Message.id, not null, `ON DELETE CASCADE`), `document_chunk_id` (FK → DocumentChunk.id, not null).

---

## 4. Especificación de la API

El backend expone una API REST (FastAPI, documentada automáticamente vía OpenAPI/Swagger). A continuación se describen los 3 endpoints principales del flujo core.

### 4.1. Registro y acceso de usuarios

Los siguientes endpoints de autenticación son necesarios para que el sistema funcione con JWT, tal como se describe en la sección 2.5 (Seguridad).

```yaml
openapi: 3.0.0
paths:
  /auth/register:
    post:
      summary: Registra un nuevo usuario (docente o estudiante)
      tags: [Auth]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [name, email, password, role]
              properties:
                name:
                  type: string
                email:
                  type: string
                  format: email
                password:
                  type: string
                  format: password
                role:
                  type: string
                  enum: [teacher, student]
      responses:
        '201':
          description: Usuario registrado correctamente
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    format: uuid
                  email:
                    type: string
                  role:
                    type: string
        '409':
          description: El email ya está registrado

  /auth/login:
    post:
      summary: Autentica un usuario y devuelve un token JWT
      tags: [Auth]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  format: password
      responses:
        '200':
          description: Login exitoso
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  token_type:
                    type: string
                    example: bearer
        '401':
          description: Credenciales inválidas
```

### 4.2. Subir material de una asignatura

```yaml
openapi: 3.0.0
paths:
  /subjects/{subject_id}/documents:
    post:
      summary: Sube un documento de material a una asignatura (rol docente)
      tags: [Documents]
      security:
        - bearerAuth: []
      parameters:
        - name: subject_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        '201':
          description: Documento procesado e indexado correctamente
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    format: uuid
                  filename:
                    type: string
                  chunks_created:
                    type: integer
        '403':
          description: El usuario no es docente de esta asignatura
```

**Ejemplo de respuesta:**
```json
{
  "id": "3f1a9c2e-1234-4a5b-8c9d-abcdef123456",
  "filename": "unidad1-introduccion.pdf",
  "chunks_created": 18
}
```

### 4.2. Consultar al asistente (chat RAG)

```yaml
openapi: 3.0.0
paths:
  /chat:
    post:
      summary: Envía una pregunta sobre una asignatura y recibe una respuesta generada con RAG
      tags: [Chat]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [subject_id, message]
              properties:
                subject_id:
                  type: string
                  format: uuid
                conversation_id:
                  type: string
                  format: uuid
                  nullable: true
                message:
                  type: string
      responses:
        '200':
          description: Respuesta generada por el asistente
          content:
            application/json:
              schema:
                type: object
                properties:
                  conversation_id:
                    type: string
                    format: uuid
                  answer:
                    type: string
                  sources:
                    type: array
                    items:
                      type: object
                      properties:
                        chunk_id:
                          type: string
                          format: uuid
                        document_id:
                          type: string
                          format: uuid
                        filename:
                          type: string
                        fragment:
                          type: string
```

**Ejemplo de petición:**
```json
{
  "subject_id": "b2c3d4e5-1111-2222-3333-abcdef123456",
  "message": "¿Qué diferencia hay entre RAG y fine-tuning?"
}
```

**Ejemplo de respuesta:**
```json
{
  "conversation_id": "9a8b7c6d-4444-5555-6666-abcdef123456",
  "answer": "Según el material de la unidad 1, RAG recupera contexto relevante en tiempo de consulta sin modificar los pesos del modelo, mientras que el fine-tuning reentrena el modelo con datos específicos...",
  "sources": [
    {
      "chunk_id": "a1b2c3d4-0001-0001-0001-abcdef123456",
      "document_id": "3f1a9c2e-1234-4a5b-8c9d-abcdef123456",
      "filename": "unidad1-introduccion.pdf",
      "fragment": "RAG recupera contexto relevante en tiempo de consulta sin modificar los pesos del modelo..."
    },
    {
      "chunk_id": "a1b2c3d4-0002-0002-0002-abcdef123456",
      "document_id": "3f1a9c2e-1234-4a5b-8c9d-abcdef123456",
      "filename": "unidad1-introduccion.pdf",
      "fragment": "El fine-tuning, en cambio, reentrena el modelo con datos específicos del dominio..."
    }
  ]
}
```

### 4.3. Eliminar historial de conversación (GDPR)

```yaml
openapi: 3.0.0
paths:
  /conversations/{conversation_id}:
    delete:
      summary: Elimina una conversación y sus mensajes asociados (derecho al olvido)
      tags: [Conversations]
      security:
        - bearerAuth: []
      parameters:
        - name: conversation_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: Conversación eliminada correctamente
        '403':
          description: El usuario no es dueño de esta conversación
        '404':
          description: Conversación no encontrada
```

---

## 5. Historias de Usuario

> Documenta 3 de las historias de usuario principales utilizadas durante el desarrollo, teniendo en cuenta las buenas prácticas de producto al respecto.

**Historia de Usuario 1 — Carga de material de asignatura**

**Prioridad:** Must-have

**Como** docente,
**quiero** subir documentos (PDF/texto) al material de mi asignatura,
**para que** el asistente pueda responder dudas de mis estudiantes basándose en mi contenido oficial.

**Criterios de aceptación (Gherkin):**

```gherkin
Escenario: Carga exitosa de material
  Dado que soy un docente autenticado y soy titular de la asignatura "Introducción a IA"
  Cuando subo un archivo PDF con el contenido de la unidad 1
  Entonces el sistema procesa el documento (chunking + embeddings) sin intervención manual
  Y recibo una confirmación con la cantidad de fragmentos indexados

Escenario: Intento de carga en asignatura ajena
  Dado que soy un docente autenticado que no es titular de la asignatura "Cálculo II"
  Cuando intento subir un documento a esa asignatura
  Entonces el sistema rechaza la operación con un error 403

Escenario: Formato de archivo no soportado
  Dado que soy un docente autenticado y titular de la asignatura
  Cuando intento subir un archivo con un formato no soportado (ej. .exe)
  Entonces el sistema rechaza el archivo y muestra un mensaje de error claro
```

---

**Historia de Usuario 2 — Consulta al asistente académico (RAG)**

**Prioridad:** Must-have

**Como** estudiante,
**quiero** preguntar dudas sobre el contenido de una asignatura,
**para que** reciba una respuesta basada en el material oficial del curso, con la fuente citada, sin depender de la disponibilidad del docente.

**Criterios de aceptación (Gherkin):**

```gherkin
Escenario: Pregunta con material disponible
  Dado que soy un estudiante autenticado
  Y la asignatura "Introducción a IA" tiene material indexado
  Cuando envío la pregunta "¿Qué diferencia hay entre RAG y fine-tuning?"
  Entonces recibo una respuesta generada a partir del material de esa asignatura
  Y la respuesta incluye referencias a los fragmentos de origen utilizados

Escenario: Pregunta sin material cargado aún
  Dado que soy un estudiante autenticado
  Y la asignatura seleccionada no tiene material indexado
  Cuando envío una pregunta
  Entonces el sistema me informa que todavía no hay material disponible para esa asignatura,
  en lugar de generar una respuesta sin fuente verificable

Escenario: Continuación de una conversación existente
  Dado que ya tengo una conversación abierta en una asignatura
  Cuando envío una nueva pregunta relacionada
  Entonces la respuesta se genera teniendo en cuenta el historial de esa conversación

Escenario (opcional - control de alucinaciones): Pregunta sin fragmentos relevantes
  Dado que soy un estudiante autenticado
  Y la asignatura tiene material indexado
  Pero ningún fragmento supera el umbral de similitud mínimo para la pregunta realizada
  Cuando envío la pregunta
  Entonces el sistema me informa que no encontró información relevante en el material disponible,
  en lugar de generar una respuesta sin respaldo documental
```

---

**Historia de Usuario 3 — Eliminación de historial de conversación (GDPR)**

**Prioridad:** Must-have

**Como** estudiante,
**quiero** poder eliminar mi historial de conversaciones con el asistente,
**para que** pueda ejercer mi derecho al olvido sobre mis datos personales.

**Criterios de aceptación (Gherkin):**

```gherkin
Escenario: Eliminación exitosa de una conversación propia
  Dado que soy un estudiante autenticado con una conversación existente
  Cuando solicito eliminar esa conversación
  Entonces el sistema borra la conversación y todos sus mensajes asociados
  Y la operación no puede deshacerse

Escenario: Intento de eliminar una conversación ajena
  Dado que soy un estudiante autenticado
  Cuando intento eliminar una conversación que pertenece a otro estudiante
  Entonces el sistema rechaza la operación con un error 403

Escenario: Eliminación de conversación inexistente
  Dado que soy un estudiante autenticado
  Cuando solicito eliminar una conversación con un identificador que no existe
  Entonces el sistema responde con un error 404
```

---

## 6. Tickets de Trabajo

> Documenta 3 de los tickets de trabajo principales del desarrollo, uno de backend, uno de frontend, y uno de bases de datos. Da todo el detalle requerido para desarrollar la tarea de inicio a fin teniendo en cuenta las buenas prácticas al respecto. 

**Ticket 1 — [BACKEND] Implementar endpoint `POST /chat` con pipeline RAG**

**Historia de usuario relacionada:** HU-2 (Consulta al asistente académico)

**Descripción:** Implementar el endpoint `POST /chat`, que recibe una pregunta de un estudiante sobre una asignatura y devuelve una respuesta generada mediante RAG, citando el documento de origen.

**Tareas técnicas:**
- Crear router `chat.py` en `api/v1/endpoints/` con el endpoint `POST /chat`, validado con un schema Pydantic (`subject_id`, `conversation_id` opcional, `message`).
- Implementar `RAGService.answer(subject_id, message, conversation_id)`:
  - Generar embedding de la pregunta (HuggingFace `paraphrase-multilingual-MiniLM-L12-v2`).
  - Recuperar los N fragmentos más relevantes de `DocumentChunk` para esa asignatura vía `DocumentChunkRepository` (similitud coseno sobre pgvector, índice hnsw).
  - Construir el prompt con el contexto recuperado (LangChain) e invocar Gemini (modelo configurable, por defecto `gemini-3.5-flash-lite`).
  - Persistir los mensajes (pregunta + respuesta) en `Conversation`/`Message` y las fuentes en `MessageSource` vía `ConversationRepository`.
- Manejar el caso de asignatura sin material indexado (respuesta controlada, no error 500).
- Proteger el endpoint con autenticación JWT (rol estudiante).
- Tests unitarios de `RAGService` con mocks del LLM y del repositorio de chunks; test de integración del endpoint con base de datos de test.

**Criterios de aceptación:**
- Dada una asignatura con material indexado, al enviar una pregunta se recibe una respuesta con un array `sources` no vacío (múltiples fragmentos citados).
- Dada una asignatura sin material, se recibe una respuesta controlada indicando que no hay contenido disponible (no un error).
- El endpoint rechaza con 401 a usuarios no autenticados.

**Estimación:** 8 puntos (talla M/L) · **Dependencias:** Ticket 3 (esquema de `Document` con pgvector debe existir antes).

---

**Ticket 2 — [FRONTEND] Interfaz de chat por asignatura**

**Historia de usuario relacionada:** HU-2 (Consulta al asistente académico)

**Descripción:** Construir la pantalla de chat donde el estudiante selecciona una asignatura, escribe preguntas y visualiza las respuestas del asistente junto con la fuente citada.

**Tareas técnicas:**
- Crear página `pages/ChatPage.tsx`, accesible desde el listado de asignaturas del estudiante.
- Componente `ChatWindow` con lista de mensajes (usuario/asistente) y input de texto.
- Componente `MessageBubble` que renderiza el contenido y, si existen, chips/links con las fuentes citadas (`sources[].filename` + fragmento).
- Hook `useChat(subjectId)` (React Query) que llama a `POST /chat` vía `services/chatService.ts` (Axios), maneja estado de carga y error.
- Estado de "escribiendo..." mientras se espera la respuesta del backend.
- Manejo de error visible si el backend responde que no hay material indexado para la asignatura.
- Tests de componente (Vitest + React Testing Library) para `ChatWindow` y `MessageBubble`.

**Criterios de aceptación:**
- El estudiante puede enviar una pregunta y ver la respuesta renderizada con la fuente citada, si existe.
- Mientras se espera la respuesta, se muestra un indicador de carga (no queda la UI congelada ni duplicable el envío).
- Si el backend indica que no hay material disponible, se muestra un mensaje claro en la propia conversación (no un error genérico).

**Estimación:** 5 puntos (talla M) · **Dependencias:** Ticket 1 (endpoint `/chat` debe estar disponible, al menos con mock).

---

**Ticket 3 — [BASE DE DATOS] Esquema de `Document`, `DocumentChunk` y `MessageSource` con soporte de embeddings (pgvector)**

**Historia de usuario relacionada:** HU-1 y HU-2 (base necesaria para carga de material y para consulta RAG)

**Descripción:** Crear las migraciones de base de datos para las tablas `documents` (metadatos del archivo), `document_chunks` (fragmentos con embeddings para RAG) y `message_sources` (relación entre mensajes y fragmentos citados), incluyendo el índice vectorial necesario para búsquedas por similitud eficientes.

**Tareas técnicas:**
- Habilitar la extensión `vector` en PostgreSQL (`CREATE EXTENSION IF NOT EXISTS vector;`).
- Crear migración (Alembic) para la tabla `documents`: `id` (uuid, PK), `subject_id` (uuid, FK → `subjects.id`, not null, `ON DELETE CASCADE`), `filename` (varchar, not null), `created_at` (timestamp, default now()).
- Crear migración para la tabla `document_chunks`: `id` (uuid, PK), `document_id` (uuid, FK → `documents.id`, not null, `ON DELETE CASCADE`), `content` (text, not null), `embedding` (`vector(384)`, dimensión del modelo `paraphrase-multilingual-MiniLM-L12-v2`), `created_at` (timestamp, default now()).
- Crear migración para la tabla `message_sources`: `id` (uuid, PK), `message_id` (uuid, FK → `messages.id`, not null, `ON DELETE CASCADE`), `document_chunk_id` (uuid, FK → `document_chunks.id`, not null).
- Crear índice `hnsw` sobre `document_chunks.embedding` con operador de distancia coseno (hnsw rinde mejor que ivfflat con pocos datos, adecuado para el MVP).
- Definir los modelos SQLAlchemy `Document`, `DocumentChunk`, `MessageSource` y el repositorio `DocumentChunkRepository` con el método `find_similar(subject_id, query_embedding, top_k)`.
- Seed de datos de prueba (algunos documentos con chunks y embeddings precalculados) para poder probar el flujo end-to-end sin depender de la carga real.

**Criterios de aceptación:**
- Las migraciones se ejecutan sin errores sobre una base de datos limpia y son reversibles (`downgrade`).
- `DocumentChunkRepository.find_similar` devuelve los fragmentos ordenados por similitud (menor distancia coseno primero), filtrados por la asignatura del documento padre.
- Eliminar una asignatura elimina en cascada sus documentos y fragmentos asociados.
- Eliminar un mensaje elimina en cascada sus `MessageSource` asociados.

**Estimación:** 5 puntos (talla M) · **Dependencias:** ninguna (ticket base, primero en el orden de ejecución).

---

## 7. Pull Requests

> Documenta 3 de las Pull Requests realizadas durante la ejecución del proyecto

Pendiente: esta es la Entrega 1 (documentación técnica, sin código todavía). Las Pull Requests se documentarán a partir de la Entrega 2, cuando exista desarrollo real sobre el repositorio.

**Pull Request 1**

**Pull Request 2**

**Pull Request 3**

