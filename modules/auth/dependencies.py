from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from common.exceptions import UnauthorizedException, ForbiddenException
from core.security import JwtService
from db.database import get_db
from modules.auth.repository import AuthRepository
from modules.auth.service import AuthService
from modules.users.models import User
from modules.users.role import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# dependency injection
def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)


# dependency injection
def get_auth_service(
    repository: AuthRepository = Depends(get_auth_repository),
    db: Session = Depends(get_db),
) -> AuthService:
    return AuthService(repository, db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = JwtService.decode_token(token)
    except ValueError:
        raise UnauthorizedException(
            message="Invalid or expired token",
            error_code="INVALID_TOKEN",
        )

    if payload.get("type") != "access":
        raise UnauthorizedException(
            message="Invalid token type",
            error_code="INVALID_TOKEN_TYPE",
        )

    user_id = payload.get("sub")
    repository = AuthRepository(db)
    user = repository.find_by_id(user_id)

    if not user:
        raise UnauthorizedException(
            message="User not found",
            error_code="USER_NOT_FOUND",
        )

    return user


# --- Authorization Dependencies ---

def require_roles(*roles: Role):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                message="Insufficient permissions",
                error_code="FORBIDDEN",
            )
        return current_user
    return dependency


require_admin = require_roles(
    Role.ROLE_ADMIN,
)

require_user = require_roles(
    Role.ROLE_ADMIN,
    Role.ROLE_USER,
)
