from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Orígenes permitidos por CORS, separados por comas (en producción: la URL pública del frontend)
    CORS_ORIGINS: str = DEFAULT_CORS_ORIGINS
    # Similitud coseno mínima (0-1) para usar un fragmento; None desactiva el filtro
    SIMILARITY_THRESHOLD: float | None = None
    # Solo para pruebas E2E: sustituye a Gemini por una respuesta fija. No definir en producción.
    LLM_FAKE: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("SIMILARITY_THRESHOLD", mode="before")
    @classmethod
    def _empty_threshold_means_disabled(cls, value):
        # una variable de entorno definida pero vacía (habitual en paneles de despliegue) equivale a no definirla
        return None if isinstance(value, str) and not value.strip() else value

    @property
    def cors_origins_list(self) -> list[str]:
        """Orígenes CORS limpios. Se descarta el comodín: con credenciales no está permitido."""
        origins = [o.strip().rstrip("/") for o in self.CORS_ORIGINS.split(",")]
        return [o for o in origins if o and o != "*"] or DEFAULT_CORS_ORIGINS.split(",")


settings = Settings()
