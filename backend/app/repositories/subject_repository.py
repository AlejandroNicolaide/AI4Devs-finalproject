import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subject import Subject


class SubjectRepository:
    def create(self, db: Session, subject_data: dict) -> Subject:
        subject = Subject(**subject_data)
        db.add(subject)
        db.commit()
        db.refresh(subject)
        return subject

    def get_all(self, db: Session) -> list[Subject]:
        return list(db.scalars(select(Subject).order_by(Subject.created_at.desc())))

    def get_by_id(self, db: Session, subject_id: uuid.UUID) -> Subject | None:
        return db.get(Subject, subject_id)

    def get_by_teacher_id(self, db: Session, teacher_id: uuid.UUID) -> list[Subject]:
        return list(
            db.scalars(
                select(Subject).where(Subject.teacher_id == teacher_id).order_by(Subject.created_at.desc())
            )
        )
