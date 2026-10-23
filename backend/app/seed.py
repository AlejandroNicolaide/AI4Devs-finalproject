"""Datos de demostración: docente, estudiante y una asignatura con material ya indexado.

Uso (desde backend/, con la base migrada):  python -m app.seed
Es idempotente: se puede ejecutar varias veces sin duplicar datos.
"""

from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService, EmailAlreadyRegisteredError
from app.services.document_service import DocumentService
from app.services.subject_service import SubjectService

TEACHER = {"name": "Docente Demo", "email": "docente@asistenteia.com", "password": "Docente123!", "role": "teacher"}
STUDENT = {"name": "Estudiante Demo", "email": "estudiante@asistenteia.com", "password": "Estudiante123!", "role": "student"}

SUBJECT_NAME = "Biología celular (demo)"
SUBJECT_DESCRIPTION = "Asignatura de ejemplo con material sobre fotosíntesis y respiración celular."
SAMPLE_FILENAME = "biologia_celular.txt"
SAMPLE_TEXT = """La fotosíntesis es el proceso por el cual las plantas, las algas y algunas bacterias convierten la
energía de la luz solar en energía química. Ocurre en los cloroplastos y produce glucosa y oxígeno a partir de
dióxido de carbono y agua.

La clorofila es el pigmento verde que absorbe la luz, principalmente en las longitudes de onda roja y azul.
Se encuentra en los tilacoides de los cloroplastos.

La fotosíntesis tiene dos fases. En la fase luminosa se genera ATP y NADPH a partir de la luz. En el ciclo de
Calvin, que no necesita luz de forma directa, esos compuestos se usan para fijar el dióxido de carbono y
producir glucosa.

La respiración celular ocurre en las mitocondrias. Su función es degradar la glucosa en presencia de oxígeno
para producir ATP, la principal moneda energética de la célula. Sus etapas son la glucólisis, el ciclo de Krebs
y la cadena de transporte de electrones.

La mitosis es el proceso de división celular que da lugar a dos células hijas genéticamente idénticas. Sus
fases son profase, metafase, anafase y telofase.
"""


def _ensure_user(db, auth_service: AuthService, user_repository: UserRepository, data: dict):
    try:
        user = auth_service.register(db, data)
        print(f"  creado usuario {data['email']} ({data['role']})")
    except EmailAlreadyRegisteredError:
        user = user_repository.get_by_email(db, data["email"])
        print(f"  ya existía {data['email']}")
    return user


def run() -> None:
    auth_service = AuthService()
    user_repository = UserRepository()
    subject_service = SubjectService()
    document_service = DocumentService()

    with SessionLocal() as db:
        print("Usuarios:")
        teacher = _ensure_user(db, auth_service, user_repository, TEACHER)
        _ensure_user(db, auth_service, user_repository, STUDENT)

        print("Asignatura:")
        existing = [
            s for s in subject_service.list_subjects(db) if s.name == SUBJECT_NAME and s.teacher_id == teacher.id
        ]
        if existing:
            print(f"  ya existía «{SUBJECT_NAME}»")
            return
        subject = subject_service.create_subject(
            db, teacher.id, {"name": SUBJECT_NAME, "description": SUBJECT_DESCRIPTION}
        )
        print(f"  creada «{SUBJECT_NAME}»")
        print("  indexando material de ejemplo (la primera vez descarga el modelo de embeddings)…")
        _, chunks = document_service.upload_document(
            db, subject.id, teacher.id, SAMPLE_FILENAME, SAMPLE_TEXT.encode("utf-8")
        )
        print(f"  documento «{SAMPLE_FILENAME}» cargado: {chunks} fragmentos")


if __name__ == "__main__":
    run()
