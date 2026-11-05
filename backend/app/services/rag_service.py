import uuid
from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.embeddings import get_embeddings
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.conversation_service import ConversationService
from app.services.subject_service import SubjectService

TOP_K = 5
HISTORY_MESSAGES = 6  # mensajes previos de la conversación que se envían al modelo

NO_MATERIAL_ANSWER = (
    "Esta asignatura todavía no tiene material disponible, por lo que no puedo responder "
    "tu pregunta. Consulta de nuevo cuando el docente haya subido contenido."
)

NO_RELEVANT_ANSWER = (
    "No encontré información relevante sobre tu pregunta en el material de esta asignatura. "
    "Prueba a reformularla o consulta directamente con el docente."
)

SYSTEM_PROMPT = (
    "Eres un asistente académico. Responde a la pregunta del estudiante usando EXCLUSIVAMENTE "
    "los fragmentos de material de la asignatura que se te proporcionan. Si los fragmentos no "
    "contienen la información necesaria, dilo claramente en lugar de inventar una respuesta. "
    "Responde en el mismo idioma de la pregunta, de forma clara y concisa."
)


class LLMUnavailableError(Exception):
    pass


class SubjectMismatchError(Exception):
    pass


@dataclass
class Source:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    fragment: str


@dataclass
class RAGAnswer:
    conversation_id: uuid.UUID
    answer: str
    sources: list[Source]


class RAGService:
    def __init__(
        self,
        chunk_repository: DocumentChunkRepository | None = None,
        document_repository: DocumentRepository | None = None,
        conversation_repository: ConversationRepository | None = None,
        subject_service: SubjectService | None = None,
        conversation_service: ConversationService | None = None,
    ):
        self.chunk_repository = chunk_repository or DocumentChunkRepository()
        self.document_repository = document_repository or DocumentRepository()
        self.conversation_repository = conversation_repository or ConversationRepository()
        self.subject_service = subject_service or SubjectService()
        self.conversation_service = conversation_service or ConversationService()

    @staticmethod
    def _build_prompt(
        message: str,
        context: list[tuple[str, str]],
        history: list[tuple[str, str]] | None = None,
    ) -> list:
        """`history` son pares (role, content) previos de la conversación, en orden cronológico."""
        fragments = "\n\n".join(
            f"[Fragmento {i}] (fuente: {filename})\n{content}"
            for i, (filename, content) in enumerate(context, 1)
        )
        previous = [
            HumanMessage(content=text) if role == "user" else AIMessage(content=text)
            for role, text in (history or [])
        ]
        human = f"Fragmentos del material:\n\n{fragments}\n\nPregunta del estudiante: {message}"
        return [SystemMessage(content=SYSTEM_PROMPT), *previous, HumanMessage(content=human)]

    @staticmethod
    def _call_llm(prompt: list) -> str:
        if not settings.GEMINI_API_KEY:
            raise LLMUnavailableError("GEMINI_API_KEY no configurada")
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2,
            timeout=60,
            max_retries=1,
        )
        try:
            return llm.invoke(prompt).text
        except Exception as exc:  # errores de red / cuota / API del proveedor
            raise LLMUnavailableError(str(exc)) from exc

    def _resolve_conversation(
        self,
        db: Session,
        user_id: uuid.UUID,
        subject_id: uuid.UUID,
        conversation_id: uuid.UUID | None,
    ):
        if conversation_id is None:
            return self.conversation_repository.create(db, user_id, subject_id)
        conversation = self.conversation_service.get_owned_conversation(db, user_id, conversation_id)
        if conversation.subject_id != subject_id:
            raise SubjectMismatchError()
        return conversation

    def answer(
        self,
        db: Session,
        user_id: uuid.UUID,
        subject_id: uuid.UUID,
        message: str,
        conversation_id: uuid.UUID | None = None,
    ) -> RAGAnswer:
        self.subject_service.get_subject(db, subject_id)  # SubjectNotFoundError si no existe
        conversation = self._resolve_conversation(db, user_id, subject_id, conversation_id)

        # el historial se lee antes de persistir la pregunta actual para no duplicarla en el prompt
        history: list[tuple[str, str]] = []
        if conversation_id is not None:
            previous = self.conversation_service.get_recent_messages(db, conversation.id, HISTORY_MESSAGES)
            history = [(m.role, m.content) for m in previous]

        chunks = []
        filenames: dict[uuid.UUID, str] = {}

        # (1) sin material -> respuesta controlada, sin llamar al LLM
        if self.chunk_repository.count_by_subject_id(db, subject_id) == 0:
            answer_text = NO_MATERIAL_ANSWER
        else:
            # (2) embedding de la pregunta, (3) búsqueda top-k por coseno
            query_embedding = get_embeddings().embed_query(message)
            scored = self.chunk_repository.find_similar(db, subject_id, query_embedding, TOP_K)
            threshold = settings.SIMILARITY_THRESHOLD
            if threshold is not None:  # similitud coseno = 1 - distancia
                scored = [(c, d) for c, d in scored if 1 - d >= threshold]
            chunks = [c for c, _ in scored]
            if not chunks:
                # (3b) ningún fragmento relevante -> respuesta controlada, sin llamar al LLM
                answer_text = NO_RELEVANT_ANSWER
            else:
                documents = self.document_repository.get_by_ids(db, list({c.document_id for c in chunks}))
                filenames = {d.id: d.filename for d in documents}
                # (4) prompt + (5) Gemini
                context = [(filenames[c.document_id], c.content) for c in chunks]
                try:
                    answer_text = self._call_llm(self._build_prompt(message, context, history))
                except LLMUnavailableError:
                    db.rollback()  # descarta la conversación recién creada
                    raise

        # (6) persistencia de mensajes y fuentes
        self.conversation_repository.add_message(db, conversation.id, "user", message)
        assistant_msg = self.conversation_repository.add_message(
            db, conversation.id, "assistant", answer_text
        )
        self.conversation_repository.add_message_sources(db, assistant_msg.id, [c.id for c in chunks])
        db.commit()

        sources = [
            Source(
                chunk_id=c.id,
                document_id=c.document_id,
                filename=filenames[c.document_id],
                fragment=c.content,
            )
            for c in chunks
        ]
        return RAGAnswer(conversation_id=conversation.id, answer=answer_text, sources=sources)
