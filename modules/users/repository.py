from sqlalchemy.orm import Session

from common.base_repository import BaseRepository
from modules.users.models import User


class UserRepository(BaseRepository[User]):
    # dependency injection
    def __init__(self, db: Session):
        super().__init__(User, db)


