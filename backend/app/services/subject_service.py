import uuid

from sqlalchemy.orm import Session

from app.models.subject import Subject
from app.repositories.subject_repository import SubjectRepository


class SubjectNotFoundError(Exception):
    pass


class SubjectService:
    def __init__(self, subject_repository: SubjectRepository | None = None):
        self.subject_repository = subject_repository or SubjectRepository()

    def create_subject(self, db: Session, teacher_id: uuid.UUID, data: dict) -> Subject:
        return self.subject_repository.create(
            db,
            {
                "name": data["name"],
                "description": data.get("description"),
                "teacher_id": teacher_id,
            },
        )

    def list_subjects(self, db: Session) -> list[Subject]:
        return self.subject_repository.get_all(db)

    def get_subject(self, db: Session, subject_id: uuid.UUID) -> Subject:
        subject = self.subject_repository.get_by_id(db, subject_id)
        if subject is None:
            raise SubjectNotFoundError(str(subject_id))
        return subject
