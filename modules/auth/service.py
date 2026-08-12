from sqlalchemy.orm import Session

from common.exceptions import ConflictException, UnauthorizedException
from core.security import PasswordService, JwtService
from modules.auth.repository import AuthRepository
from modules.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from modules.users.models import User
from modules.users.role import Role


class AuthService:
    def __init__(self, repository: AuthRepository, db: Session):
        self.repository = repository
        self.db = db

    def register(self, request: RegisterRequest) -> UserResponse:
        existing = self.repository.find_by_email(request.email)
        if existing:
            raise ConflictException(
                message="Email already registered",
                error_code="EMAIL_DUPLICATE",
            )

        hashed_password = PasswordService.hash(request.password)

        user = User(
            email=request.email,
            password_hash=hashed_password,
            role=Role.ROLE_USER,
        )

        self.repository.save(user)
        self.db.commit()
        self.db.refresh(user)

        return UserResponse.model_validate(user)

    def login(self, request: LoginRequest) -> TokenResponse:
        user = self.repository.find_by_email(request.email)
        if not user:
            raise UnauthorizedException(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
            )

        if not PasswordService.verify_password(request.password, user.password_hash):
            raise UnauthorizedException(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
            )

        access_token = JwtService.create_access_token(str(user.id))
        refresh_token = JwtService.create_refresh_token(str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def refresh(self, request: RefreshRequest) -> TokenResponse:
        try:
            payload = JwtService.decode_token(request.refresh_token)
        except ValueError:
            raise UnauthorizedException(
                message="Invalid refresh token",
                error_code="INVALID_TOKEN",
            )

        if payload.get("type") != "refresh":
            raise UnauthorizedException(
                message="Invalid token type",
                error_code="INVALID_TOKEN_TYPE",
            )

        user_id = payload.get("sub")
        user = self.repository.find_by_id(user_id)
        if not user:
            raise UnauthorizedException(
                message="User not found",
                error_code="USER_NOT_FOUND",
            )

        access_token = JwtService.create_access_token(str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
        )

    def get_me(self, user_id: str) -> UserResponse:
        user = self.repository.find_by_id(user_id)
        if not user:
            raise UnauthorizedException(
                message="User not found",
                error_code="USER_NOT_FOUND",
            )

        return UserResponse.model_validate(user)
