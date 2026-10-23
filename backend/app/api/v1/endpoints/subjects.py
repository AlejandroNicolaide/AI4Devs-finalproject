import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser, CurrentTeacher
from app.schemas.subject import SubjectCreate, SubjectResponse
from app.services.subject_service import SubjectNotFoundError, SubjectService

router = APIRouter(prefix="/subjects", tags=["Subjects"])

subject_service = SubjectService()


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(teacher: CurrentTeacher, data: SubjectCreate, db: Session = Depends(get_db)):
    return subject_service.create_subject(db, teacher.id, data.model_dump())


@router.get("", response_model=list[SubjectResponse])
def list_subjects(_: CurrentUser, db: Session = Depends(get_db)):
    return subject_service.list_subjects(db)


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(_: CurrentUser, subject_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return subject_service.get_subject(db, subject_id)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")
