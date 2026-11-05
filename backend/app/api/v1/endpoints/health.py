from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    """Comprobación de disponibilidad para la plataforma de despliegue (sin autenticación)."""
    return {"status": "ok"}
