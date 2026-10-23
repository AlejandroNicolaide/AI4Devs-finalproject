import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentTeacher
from app.schemas.document import DocumentListItem, DocumentResponse
from app.services.document_service import (
    DocumentService,
    EmptyDocumentError,
    NotSubjectOwnerError,
    UnsupportedFileTypeError,
)
from app.services.subject_service import SubjectNotFoundError

router = APIRouter(prefix="/subjects/{subject_id}/documents", tags=["Documents"])

document_service = DocumentService()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(teacher: CurrentTeacher, subject_id: uuid.UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        document, chunks_created = document_service.upload_document(
            db, subject_id, teacher.id, file.filename or "", content
        )
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")
    except NotSubjectOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No eres titular de esta asignatura")
    except UnsupportedFileTypeError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no soportado. Formatos aceptados: PDF, TXT",
        )
    except EmptyDocumentError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se pudo extraer texto del documento",
        )
    return DocumentResponse(id=document.id, filename=document.filename, chunks_created=chunks_created)


@router.get("", response_model=list[DocumentListItem])
def list_documents(teacher: CurrentTeacher, subject_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return document_service.list_documents(db, subject_id, teacher.id)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignatura no encontrada")
    except NotSubjectOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No eres titular de esta asignatura")
