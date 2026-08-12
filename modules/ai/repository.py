from sqlalchemy import select
from sqlalchemy.orm import Session

from common.base_repository import BaseRepository
from modules.users.models import User


class AuthRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def find_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)
