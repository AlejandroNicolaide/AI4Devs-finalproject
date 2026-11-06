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

Pendiente de completar con la URL pública del despliegue en Dokploy (ver 2.4): `https://app.<tu-dominio>`. Mientras tanto, el proyecto se puede levantar en local con las instrucciones de 1.4 y las credenciales de prueba incluidas.

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
- **Control de alucinaciones (opcional, implementado):** umbral de similitud mínimo configurable (`SIMILARITY_THRESHOLD`, ver 1.4); si ningún fragmento recuperado lo supera, el asistente responde que no encontró información relevante en el material y no llama al modelo. Viene desactivado por defecto.
- **Contexto de la conversación:** en una conversación existente, el asistente recibe también los últimos mensajes para poder responder preguntas de seguimiento («¿y en cuál de ellas…?»).

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
python -m app.seed               # usuarios de prueba + asignatura demo con material indexado
uvicorn app.main:app --reload    # http://localhost:8000  (docs en /docs)

# 4. Frontend (otra terminal)
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

**Variables de entorno (`backend/.env`):** `DATABASE_URL` (por defecto `postgresql+psycopg2://postgres:postgres@localhost:5434/asistenteia`), `SECRET_KEY`, `GEMINI_API_KEY` y `GEMINI_MODEL` (por defecto `gemini-3.5-flash-lite`; `gemini-2.5-flash` ya no está disponible para cuentas nuevas de Google AI Studio).

Variables opcionales:
- `CORS_ORIGINS`: orígenes permitidos por CORS, separados por comas (por defecto, los dos orígenes del frontend local; en producción, la URL pública del frontend). Un `*` se ignora porque la API usa credenciales.
- `SIMILARITY_THRESHOLD`: similitud coseno mínima (0-1) para citar un fragmento. Vacío (por defecto) = sin filtro. Si ningún fragmento lo supera, el asistente responde que no encontró información relevante en el material y no llama a Gemini. Calibrado con el material de demostración y el modelo de embeddings real: las preguntas relevantes obtienen entre 0,19 y 0,81 y las ajenas al temario no pasan de 0,10, por lo que **0,15** es un valor conservador. Con más material y fragmentos más pequeños conviene recalibrarlo.

**Notas:**
- La primera subida de un documento descarga el modelo de embeddings de HuggingFace (~460 MB, puede tardar unos minutos); después queda en caché.
- Sin `GEMINI_API_KEY` el resto de la aplicación funciona, pero `/chat` responde 503 en asignaturas con material.
- Los datos de demostración se cargan con `python -m app.seed` (desde `backend/`, con la base ya migrada). Es idempotente y la primera vez descarga el modelo de embeddings.

**Credenciales de prueba** (creadas por `python -m app.seed`):

| Rol | Email | Contraseña |
|---|---|---|
| Docente | `docente@asistenteia.com` | `Docente123!` |
| Estudiante | `estudiante@asistenteia.com` | `Estudiante123!` |

El seed también crea la asignatura «Biología celular (demo)» con un documento ya indexado (`biologia_celular.txt`), así que el estudiante puede preguntar de inmediato (por ejemplo: «¿Cuáles son las fases de la mitosis?»). También puedes crear tus propios usuarios desde `/register`. Estas credenciales son solo para desarrollo local.

**Prueba rápida:** inicia sesión como estudiante → abre «Biología celular (demo)» → «Preguntar al asistente» → revisa la respuesta y sus fuentes. Para el flujo de docente: inicia sesión como docente → crea una asignatura → sube un PDF o TXT → vuelve a entrar como estudiante y pregunta sobre su contenido.

**Más información:** cómo ejecutar los tests en 2.6 (backend 105, frontend 19, E2E 1; cobertura 92 % en backend) y cómo desplegar con Docker/Dokploy en 2.4.

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
  - `RAGService`: orquesta el pipeline RAG (chunking del material subido, generación de embeddings, recuperación de fragmentos relevantes por similitud, construcción del prompt con contexto, llamada al LLM). Incluye los últimos 6 mensajes de la conversación en el prompt y aplica, si está configurado, un umbral de similitud mínimo para evitar respuestas sin respaldo documental (control de alucinaciones).
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
    api/v1/endpoints/    # Routers FastAPI (auth, subjects, documents, chat, conversations, health)
    services/            # Lógica de negocio: auth, subject, document, rag, conversation
    repositories/        # Acceso a datos (SQLAlchemy + consultas pgvector)
    models/              # Entidades SQLAlchemy (User, Subject, Document, DocumentChunk, Conversation, Message, MessageSource)
    schemas/             # Esquemas Pydantic (request/response)
    core/                # Configuración, base de datos, seguridad (JWT), dependencias, embeddings
    seed.py              # Datos de demostración (usuarios de prueba + asignatura con material)
    main.py              # Punto de entrada de la app FastAPI
  alembic/               # Migraciones (esquema inicial + índice hnsw)
  tests/                 # unit/ (servicios con mocks) e integration/ (endpoints con Postgres+pgvector)
  scripts/init_db.sql    # Creación manual del esquema (alternativa a las migraciones)
  Dockerfile, docker-entrypoint.sh, requirements*.txt, pytest.ini
frontend/
  src/
    pages/               # Vistas (login, registro, asignaturas, detalle, chat, historial)
    components/          # Componentes de UI reutilizables (+ sus tests *.test.tsx)
    context/, hooks/     # Sesión (AuthContext) y hooks de React Query
    services/            # Llamadas a la API (Axios)
    types/               # Tipos TypeScript compartidos
  e2e/                   # Test E2E de Playwright y arranque del backend de pruebas
  Dockerfile, nginx.conf, playwright.config.ts
docker-compose.yml       # Solo Postgres+pgvector para desarrollo local
docker-compose.prod.yml  # Stack de producción para Dokploy (postgres + backend + frontend)
.github/workflows/ci.yml # CI: pytest, lint, build y vitest
openspec/                # Specs, changes y archivo del flujo spec-driven (OpenSpec)
```

La estructura del `backend` refleja directamente las capas descritas en 2.1/2.2 (API → Services → Repositories → Models), de modo que cada carpeta corresponde a una responsabilidad concreta del patrón Layered Architecture + Repository Pattern. El `frontend` sigue una organización estándar por tipo de artefacto (páginas, componentes, hooks, servicios), habitual en proyectos React con TypeScript.

### **2.4. Infraestructura y despliegue**

```mermaid
flowchart LR
    Dev["Repositorio GitHub\n(final-project-AN)"] -- "push / PR" --> CI["GitHub Actions\npytest + lint + build + vitest"]
    Dev -- "deploy (Git)" --> DK["Dokploy (VPS)\ndocker-compose.prod.yml"]
    subgraph VPS["VPS con Dokploy + Traefik (HTTPS Let's Encrypt)"]
        FE["frontend\nnginx + build de Vite"]
        BE["backend\nFastAPI + modelo de embeddings"]
        DB[("postgres\npgvector/pgvector:pg15")]
    end
    DK --> VPS
    Usuario["Usuario (docente/estudiante)"] -- "https://app.tu-dominio" --> FE
    FE -- "https://api.tu-dominio" --> BE
    BE --> DB
    BE --> LLMEXT["Gemini API"]
```

**Componentes:**
- **Orquestación:** `docker-compose.prod.yml` define tres servicios (`postgres`, `backend`, `frontend`) con volumen persistente para la base de datos y healthchecks. Se despliega como aplicación *Compose* en **Dokploy**, que construye las imágenes desde el repositorio y las publica detrás de Traefik con certificados Let's Encrypt.
- **Base de datos:** imagen `pgvector/pgvector:pg15`, la misma que en local. El Postgres gestionado de Dokploy no incluye la extensión `pgvector`, por eso se despliega como servicio del compose.
- **Backend:** `backend/Dockerfile` (Python 3.11, torch solo CPU, modelo de embeddings descargado al construir la imagen). Al arrancar ejecuta `alembic upgrade head`, carga los datos de demostración (`RUN_SEED=1`, idempotente) y lanza uvicorn. Expone `GET /health`.
- **Frontend:** `frontend/Dockerfile` en dos etapas (build de Vite → nginx con fallback de SPA). La URL de la API se incrusta en el build (`VITE_API_URL`).
- **CI:** `.github/workflows/ci.yml` ejecuta en cada push y pull request `pytest` (con un servicio `pgvector/pgvector:pg15`), `npm run lint`, `npm run build` y `npm run test`. El E2E de Playwright se ejecuta en local (ver 2.6).

#### Despliegue en Dokploy

**Requisitos:** un VPS con Dokploy instalado y **2 GB de RAM o más** (el modelo de embeddings local ocupa ~1-1,5 GB), y un dominio con dos registros DNS `A` hacia la IP del VPS: `app.<dominio>` (frontend) y `api.<dominio>` (backend).

1. En Dokploy: *Create Service → Compose*, proveedor **Git/GitHub**, repositorio `AlejandroNicolaide/AI4Devs-finalproject`, rama `final-project-AN`, *Compose Path* `./docker-compose.prod.yml`.
2. En la pestaña **Environment**, definir estas variables (no se guardan en el repositorio):

| Variable | Obligatoria | Valor |
|---|---|---|
| `POSTGRES_PASSWORD` | Sí | Contraseña de la base de datos. **Alfanumérica** (se inserta en la URL de conexión) |
| `SECRET_KEY` | Sí | Cadena aleatoria larga para firmar los JWT (por ejemplo `openssl rand -hex 32`) |
| `GEMINI_API_KEY` | Sí para el chat | API key de Google AI Studio. Sin ella el chat responde 503 |
| `CORS_ORIGINS` | Sí | URL pública del frontend, p. ej. `https://app.<dominio>` |
| `VITE_API_URL` | Sí | URL pública de la API, p. ej. `https://api.<dominio>` (se incrusta al construir el frontend) |
| `GEMINI_MODEL` | No | Por defecto `gemini-3.5-flash-lite` |
| `SIMILARITY_THRESHOLD` | No | Vacío = sin filtro; `0.15` recomendado (ver 1.4) |
| `RUN_SEED` | No | `1` (por defecto) crea los usuarios y la asignatura de demostración; `0` los omite |
| `POSTGRES_USER`, `POSTGRES_DB` | No | Por defecto `postgres` y `asistenteia` |

3. En la pestaña **Domains**, añadir `app.<dominio>` → servicio `frontend`, puerto `80`, y `api.<dominio>` → servicio `backend`, puerto `8000`, ambos con **HTTPS** y certificado *Let's Encrypt*.
4. Pulsar **Deploy**. La primera vez el backend tarda un par de minutos en responder (migra, genera los embeddings del seed y carga el modelo).
5. Comprobar `https://api.<dominio>/health` → `{"status":"ok"}` y entrar en `https://app.<dominio>` con las credenciales de prueba (ver 1.4).

**Alternativa manual para el esquema:** `backend/scripts/init_db.sql` crea todas las tablas, la extensión `vector` y el índice hnsw (equivale a las migraciones y deja `alembic_version` al día): `psql "<DATABASE_URL>" -f backend/scripts/init_db.sql`.

### **2.5. Seguridad**

- **Autenticación y roles:** acceso diferenciado por rol (docente/estudiante) mediante JWT (caducidad de 60 minutos); las contraseñas se guardan con hash bcrypt; un docente solo gestiona el material de sus propias asignaturas y un estudiante solo accede a su propio historial.
- **CORS restringido:** la API solo acepta peticiones de los orígenes definidos en `CORS_ORIGINS`.
- **Protección de datos (GDPR):**
  - Minimización de datos: solo se almacena lo estrictamente necesario para el funcionamiento (identificador de usuario, mensajes de la conversación, asignatura asociada), sin datos sensibles adicionales.
  - Consentimiento explícito: **no implementado** en esta versión (queda como mejora futura: aceptación de la política de privacidad en el registro).
  - Derecho al olvido: el estudiante puede eliminar su historial de conversaciones desde la propia aplicación (funcionalidad ya listada en 1.2).
  - Cifrado en tránsito: el navegador se comunica con el frontend y con la API exclusivamente por HTTPS (Traefik de Dokploy con certificados Let's Encrypt). La base de datos no se expone: solo es alcanzable por el backend a través de la red privada del compose.
  - Cifrado en reposo: la base de datos corre en un volumen del propio VPS, por lo que depende del cifrado de disco del servidor (no se aplica cifrado a nivel de aplicación).
  - Terceros: la pregunta del estudiante y los fragmentos recuperados se envían a la API de Gemini para generar la respuesta; los embeddings se calculan en local.
  - Retención: los datos conversacionales se conservan solo mientras la cuenta esté activa o hasta que el usuario solicite su borrado.
- **Gestión de secretos:** claves de API (Gemini) y credenciales de base de datos como variables de entorno, nunca en el repositorio.
- **Validación de entrada:** esquemas Pydantic en cada endpoint, previniendo inyección y payloads malformados antes de llegar a la capa de servicio.
- **Credenciales de demostración:** el seed (`RUN_SEED=1`, valor por defecto) crea los usuarios de prueba documentados en este README para que quien revise pueda entrar en la instancia pública. Son datos de demostración sin relación con ningún secreto real; en un despliegue real se desactiva con `RUN_SEED=0`.

**Limitaciones conocidas** (detectadas en las revisiones `/code-review` de los PRs; no bloquean el flujo del MVP y quedan como mejoras):

- La subida de documentos no limita el tamaño del archivo ni captura los PDF cifrados o corruptos (devolverían 500).
- No hay OCR: un PDF escaneado (solo imágenes) no tiene texto que indexar. Si lo único con texto es una marca repetida en todas las páginas (p. ej. «Scanned by CamScanner»), la subida se rechaza con un 422; hay que usar un PDF con texto seleccionable o un TXT.
- El registro es abierto y cualquiera puede elegir el rol `teacher`, con lo que puede crear asignaturas y subir material (no hay verificación de docentes ni inscripción: decisión de alcance del MVP).
- Dos registros simultáneos con el mismo email pueden devolver 500 en lugar de 409; la longitud máxima de la contraseña se valida en caracteres y bcrypt cuenta bytes.
- La recuperación de fragmentos usa solo el texto de la pregunta: un seguimiento muy elíptico («¿y la segunda?») puede no encontrar material aunque el historial sí se envíe al modelo.
- La transacción de base de datos permanece abierta durante la llamada a Gemini (hasta 60 s); con muchas preguntas lentas simultáneas el pool de conexiones puede agotarse.
- El orden de mensajes dentro de un mismo turno depende de un desempate por rol y no de una columna secuencial.
- Con varias réplicas del backend, la migración y el seed del arranque podrían ejecutarse a la vez; el despliegue previsto usa una sola réplica.
- `SECRET_KEY` no se valida en fuerza mínima y `LLM_FAKE` solo avisa por log si se activa; deben definirse con cuidado en el panel de Dokploy.

### **2.6. Tests**

La suite cubre los tres niveles pedidos y se traza a los escenarios Gherkin de las historias de usuario (sección 5). Ningún test llama a Gemini: en backend se sustituye la llamada al modelo y los embeddings por dobles deterministas; en el E2E se usa `LLM_FAKE=1`.

| Nivel | Herramienta | Qué cubre | Tests |
|---|---|---|---|
| Unitarios backend | Pytest | Service Layer con repositorios mockeados: `AuthService`, `RAGService` (con/sin material, historial, umbral, fallo del LLM), `DocumentService` (TXT, PDF, formatos no soportados, docente ajeno), `ConversationService` | 44 |
| Integración backend | Pytest + FastAPI `TestClient` | Endpoints reales sobre **Postgres+pgvector de test**: auth, asignaturas y carga, chat (`sources` como array, 401/403/404/503), conversaciones y borrado en cascada, índice hnsw, `/health`, CORS | 61 |
| Componentes frontend | Vitest + React Testing Library | `MessageBubble` (fuentes expandibles), `ChatWindow`, `LoginPage`, `FileUpload` | 19 |
| E2E | Playwright (Chromium) | Docente sube material → estudiante pregunta → respuesta con **Fuentes** → historial → borrado | 1 |

Cobertura del backend: **92 %** de las líneas de `app/` (`pytest --cov=app`).

**Cómo ejecutarlos** (desde la raíz, con la base de datos arriba: `docker compose up -d`):

```bash
# Backend: crea la base de test una sola vez y ejecuta unitarios + integración
docker exec asistenteia-postgres psql -U postgres -c "CREATE DATABASE asistenteia_test"
cd backend
pip install -r requirements-dev.txt
pytest --cov=app                 # TEST_DATABASE_URL opcional; por defecto localhost:5434/asistenteia_test

# Frontend: componentes
cd ../frontend
npm run test

# E2E (la primera vez: npx playwright install chromium)
npm run test:e2e
```

El E2E levanta por sí solo su propio backend (puerto 8001, base `asistenteia_e2e`, migraciones incluidas, `LLM_FAKE=1`) y su propio Vite (puerto 5174), así que no interfiere con el entorno de desarrollo (8000 / 5173). Necesita el entorno virtual del backend creado en `backend/venv` (o `E2E_PYTHON` apuntando a otro intérprete) y Postgres arriba. Usa el modelo de embeddings real, por lo que la primera ejecución tarda más.

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

El backend expone una API REST (FastAPI, documentada automáticamente vía OpenAPI/Swagger). A continuación se describen los endpoints del flujo principal (registro y acceso, carga de material, chat RAG y borrado de historial). Además existen `GET /subjects`, `GET /subjects/{id}`, `GET /subjects/{id}/documents`, `GET /conversations`, `GET /conversations/{id}/messages` y `GET /health`; la documentación interactiva completa está en `/docs`.

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
        '415':
          description: Formato no soportado (solo PDF y TXT)
        '422':
          description: No se pudo extraer texto del documento
```

**Ejemplo de respuesta:**
```json
{
  "id": "3f1a9c2e-1234-4a5b-8c9d-abcdef123456",
  "filename": "unidad1-introduccion.pdf",
  "chunks_created": 18
}
```

### 4.3. Consultar al asistente (chat RAG)

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

### 4.4. Eliminar historial de conversación (GDPR)

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

Las tres Pull Requests de la entrega final se abrieron en este mismo repositorio hacia la rama `final-project-AN`. Cada una pasó el CI de GitHub Actions y una revisión automatizada con `/code-review` de Claude Code; los hallazgos aplicados se commitearon en la propia rama del PR y los que no se corrigieron figuran como limitaciones en la sección 2.5.

**Pull Request 1 — [#1 Tests, historial en respuestas, umbral de similitud y CI](https://github.com/AlejandroNicolaide/AI4Devs-finalproject/pull/1)** (`feature/tests`)

- Historial de la conversación en el prompt (criterio de aceptación de la HU-2), umbral de similitud opcional, `GET /health` y CORS configurable.
- Suite de tests: 99 en el momento del PR (105 en la rama final) de backend (92 % de cobertura), 19 de frontend y 1 E2E con Playwright.
- Workflow de GitHub Actions con pytest sobre pgvector, lint, build y Vitest.
- Revisión `/code-review`: 10 hallazgos. Se corrigieron tres (historial que podía empezar con una respuesta del asistente, subida de documentos que bloqueaba el servidor y aviso al activar `LLM_FAKE`); el resto son limitaciones previas documentadas.

**Pull Request 2 — [#2 Despliegue en Dokploy: Dockerfiles, compose de producción y guía](https://github.com/AlejandroNicolaide/AI4Devs-finalproject/pull/2)** (`feature/deploy`)

- `Dockerfile` del backend (torch CPU y modelo precargado) y del frontend (nginx con fallback de SPA), entrypoint con migraciones y seed, y `docker-compose.prod.yml` con `pgvector/pgvector:pg15`.
- Guía de despliegue en Dokploy (variables, dominios, HTTPS, RAM necesaria).
- Revisión `/code-review`: se corrigieron el `start-period` del healthcheck y la ejecución duplicada del CI; se mantuvo el seed por defecto de forma deliberada (credenciales de demostración exigidas por la entrega).

**Pull Request 3 — [#3 Documentación final y correcciones de la revisión](https://github.com/AlejandroNicolaide/AI4Devs-finalproject/pull/3)** (`feature/docs-final`)

- README alineado con lo construido (infraestructura real, seguridad, estructura, API, tests, despliegue) y limitaciones conocidas.
- `prompts.md` ampliado con las secciones de pruebas, despliegue y mantenimiento, el resumen del flujo de IA y la tabla de IA por fase.
- Revisión `/code-review`: detectó dos fallos reales que se corrigieron en esta misma rama: una segunda pregunta en una conversación ya abierta no aparecía hasta recargar (el hook no invalidaba los mensajes; el E2E ahora cubre el seguimiento y se comprobó que falla sin el arreglo) y el seed no reintentaba el material si un arranque anterior fallaba al indexar.

