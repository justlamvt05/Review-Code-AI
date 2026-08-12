from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from modules.notifications.repository import NotificationRepository
from modules.notifications.service import NotificationService
from modules.users.repository import UserRepository
from modules.users.dependencies import get_user_repository


# dependency injection
def get_notification_repository(db: Session = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)


# dependency injection
def get_notification_service(
    repository: NotificationRepository = Depends(get_notification_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    db: Session = Depends(get_db),
) -> NotificationService:
    return NotificationService(repository, user_repository, db)
