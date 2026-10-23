# Design

## Context

Proyecto greenfield — no hay código existente. La arquitectura, el modelo de datos y el contrato de API están completamente definidos en la Entrega 1 (ver readme.md secciones 2-4 y CLAUDE.md). Esta es la primera implementación: todo se construye desde cero.

Restricciones del entorno de desarrollo:
- Windows 11, Python 3.13, Node.js 24, Docker Desktop (pgvector/pgvector:pg15)
- Sin cuenta en Supabase — base de datos local en Docker
- Gemini API key pendiente de crear (Google AI Studio, tier gratuito)

## Goals / Non-Goals

**Goals:**
- Backend FastAPI completamente funcional con las 4 capas definidas en CLAUDE.md
- Frontend React funcional con flujo completo para docente y estudiante
- Pipeline RAG operativo end-to-end (subir material → preguntar → respuesta con fuentes)
- Entorno de desarrollo reproducible con Docker Compose

**Non-Goals:**
- Despliegue en producción (Vercel/Render/Supabase) — queda para Entrega 3
- Tests automatizados (no obligatorios en Entrega 2 según la guía del máster)
- CI/CD con GitHub Actions
- Panel de analítica para docentes (marcado como should-have)
- Control de alucinaciones por umbral de similitud (marcado como nice-to-have)
- Integración con LMS/Moodle

## Decisions

### D1: Estructura del proyecto — Monorepo con carpetas independientes

**Decisión:** Un repositorio con `backend/` y `frontend/` en la raíz, cada uno con su propio package manager y configuración.

**Alternativa descartada:** Monorepo con Turborepo/Nx — añade complejidad innecesaria para un proyecto con solo 2 workspaces y un desarrollador.

**Razón:** Simplicidad. Cada parte se levanta y despliega por separado. Docker Compose orquesta todo en local.

### D2: Base de datos local con Docker

**Decisión:** `docker-compose.yml` con imagen `pgvector/pgvector:pg15`, volumen persistente para datos, puerto 5432 expuesto.

**Alternativa descartada:** Supabase cloud — requiere cuenta y configuración de red; Docker es más rápido para iterar en local y no tiene dependencias externas.

**Razón:** Cero dependencias de cuentas externas para desarrollar. La migración a Supabase (Entrega 3) es trivial: solo cambia la connection string.

### D3: Autenticación — PyJWT + passlib[bcrypt]

**Decisión:** Implementar JWT manualmente con PyJWT para generar/validar tokens, y passlib con bcrypt para hashear passwords. Dependency de FastAPI `get_current_user` como middleware.

**Alternativa descartada:** python-jose — está deprecado y no se mantiene activamente. FastAPI-Users — abstrae demasiado para un MVP con solo 2 roles.

**Razón:** PyJWT es el estándar activo, passlib+bcrypt es robusto, y el código es explícito (alineado con las 4 capas: el auth vive en `core/security.py` y un dependency en `core/deps.py`).

### D4: Procesamiento de documentos — PyPDF2 + text splitter de LangChain

**Decisión:** Usar PyPDF2 para extraer texto de PDFs, `RecursiveCharacterTextSplitter` de LangChain para chunking (chunk_size=1000, overlap=200), y `HuggingFaceEmbeddings` de langchain-huggingface para generar vectores.

**Alternativa descartada:** Unstructured.io — potente pero pesado en dependencias y overkill para PDF de texto plano académico. PyMuPDF — licencia AGPL más restrictiva.

**Razón:** PyPDF2 es ligero y suficiente para PDFs de texto. LangChain text splitter ya maneja el overlap entre chunks. El modelo de embeddings (`paraphrase-multilingual-MiniLM-L12-v2`) se ejecuta localmente sin costo por llamada.

### D5: RAG Pipeline — LangChain directo (sin ConversationalRetrievalChain)

**Decisión:** Implementar el pipeline RAG como orquestación explícita en `RAGService`:
1. Generar embedding de la query con HuggingFace
2. Buscar top-K chunks similares vía `DocumentChunkRepository.find_similar()` (consulta SQL directa con pgvector, operador `<=>` coseno)
3. Construir prompt con template (system message + contexto recuperado + pregunta)
4. Llamar a Gemini 2.5 Flash vía `langchain-google-genai` (`ChatGoogleGenerativeAI`)
5. Persistir mensajes y fuentes

**Alternativa descartada:** `ConversationalRetrievalChain` de LangChain — opaca, difícil de depurar, y mezcla responsabilidades (no respeta la separación de capas). PGVector de LangChain como retriever — abstrae la consulta SQL, pero no permite filtrar por subject_id sin workarounds.

**Razón:** Control total del flujo. Cada paso es explícito y testeable. El Repository Pattern se mantiene intacto: `DocumentChunkRepository` encapsula la consulta pgvector con filtro por asignatura. El Service Layer orquesta sin depender de abstracciones de LangChain para el retrieval.

### D6: Modelo de embeddings — Ejecución síncrona en el request

**Decisión:** Generar embeddings sincrónicamente durante el upload de documentos (chunking + embedding en el mismo request). Para el MVP, el volumen es bajo y la latencia aceptable.

**Alternativa descartada:** Celery/RQ para procesamiento asíncrono — añade infraestructura (Redis/broker) y complejidad que no se justifica para el volumen del MVP.

**Razón:** Un PDF académico genera ~20-50 chunks, el modelo local tarda ~2-5 segundos en total. El usuario (docente) puede esperar esa latencia. Si escala, se migra a procesamiento async.

### D7: Frontend — Create React App reemplazado por Vite

**Decisión:** Scaffold con Vite (`npm create vite@latest -- --template react-ts`), Tailwind CSS v3 para estilos, Headless UI para componentes accesibles, Axios + React Query (TanStack Query) para estado del servidor.

**Alternativa descartada:** Next.js — SSR innecesario para un SPA que consume una API REST. CRA — deprecated.

**Razón:** Vite es rápido en desarrollo, Tailwind permite UI consistente sin CSS custom extenso, React Query maneja cacheo y estado de las peticiones automáticamente.

### D8: Estructura de carpetas del frontend

**Decisión:**
```
frontend/src/
  pages/          -- LoginPage, SubjectsPage, SubjectDetailPage, ChatPage
  components/     -- ChatWindow, MessageBubble, FileUpload, Navbar, ProtectedRoute
  hooks/          -- useAuth, useChat, useSubjects
  services/       -- api.ts (instancia Axios), authService, subjectService, chatService
  context/        -- AuthContext (JWT token + user info)
  types/          -- interfaces TypeScript compartidas
```

**Razón:** Estructura estándar por tipo de artefacto, alineada con lo documentado en la Entrega 1. Suficiente para el tamaño del MVP sin necesidad de feature folders.

### D9: Gestión de estado de autenticación — React Context

**Decisión:** `AuthContext` almacena el token JWT y los datos del usuario en memoria (+ localStorage para persistencia entre recargas). `ProtectedRoute` redirige a login si no hay sesión. Axios interceptor inyecta el token automáticamente en cada request.

**Alternativa descartada:** Redux/Zustand — overkill para estado global tan simple (solo auth). El resto del estado es estado del servidor manejado por React Query.

**Razón:** Context API es suficiente para un único slice de estado global (auth). React Query maneja todo el estado del servidor (subjects, conversations, messages).

## Risks / Trade-offs

- **[Python 3.13 vs 3.11]** → Algunas dependencias (sentence-transformers, pgvector) pueden no estar testeadas en 3.13. **Mitigación:** Probar primero; si falla alguna dependencia, instalar Python 3.11 con pyenv-win.

- **[Embeddings sincrónicos]** → Si un docente sube un PDF muy grande (>100 páginas), el request puede tardar >30s. **Mitigación:** Para el MVP es aceptable. Se puede añadir un spinner en frontend y un timeout generoso en Axios.

- **[Sin tests en Entrega 2]** → No hay red de seguridad automatizada contra regresiones. **Mitigación:** La Entrega 2 no los exige. Se valida manualmente el flujo E2E. Los tests se implementan en la Entrega 3.

- **[HuggingFace model download]** → La primera ejecución descarga ~120MB del modelo de embeddings. **Mitigación:** Documentar en README. Solo ocurre una vez; se cachea en `~/.cache/huggingface/`.

- **[Gemini API key requerida para chat]** → Sin la key, el pipeline RAG no funciona. **Mitigación:** El resto del sistema (auth, subjects, upload+chunking) funciona sin ella. Documentar claramente en README cómo obtenerla (Google AI Studio, gratis).
