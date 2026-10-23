from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from app.models.user import User


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    def register(self, db: Session, user_data: dict) -> User:
        email = user_data["email"].lower()
        if self.user_repository.get_by_email(db, email):
            raise EmailAlreadyRegisteredError(email)
        return self.user_repository.create(
            db,
            {
                "name": user_data["name"],
                "email": email,
                "password_hash": hash_password(user_data["password"]),
                "role": user_data["role"],
            },
        )

    def login(self, db: Session, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(db, email.lower())
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token({"sub": str(user.id), "role": user.role})
