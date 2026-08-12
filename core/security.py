from pwdlib import PasswordHash
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt
from jose import JWTError
from core.config import settings

password_hash = PasswordHash.recommended()

class PasswordService:

    @staticmethod
    def hash(password: str) -> str:
        return password_hash.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return password_hash.verify(password, hashed_password)


class JwtService:

    @staticmethod
    def create_access_token(user_id: str) -> str:

        payload = {
            "sub": user_id,
            "type": "access",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC)
            + timedelta(minutes=settings.access_token_expire_minutes),
        }

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    @staticmethod
    def create_refresh_token(user_id: str) -> str:

        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC)
            + timedelta(days=settings.refresh_token_expire_days),
        }

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError as e:
            raise ValueError("Invalid token") from e