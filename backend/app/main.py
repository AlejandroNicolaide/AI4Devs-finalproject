from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth, chat, conversations, documents, health, subjects
from app.core.config import settings

app = FastAPI(title="AsistenteIA API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(conversations.router)
