from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from modules.users.repository import UserRepository
from modules.users.service import UserService


# dependency injection
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


# dependency injection
def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    db: Session = Depends(get_db),
) -> UserService:
    return UserService(repository, db)