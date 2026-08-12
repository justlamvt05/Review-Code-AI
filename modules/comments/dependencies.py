from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from modules.comments.repository import CommentRepository
from modules.comments.service import CommentService
from modules.notifications.dependencies import get_notification_service
from modules.notifications.service import NotificationService
from modules.reviews.repository import ReviewRepository
from modules.reviews.dependencies import get_review_repository


# dependency injection
def get_comment_repository(db: Session = Depends(get_db)) -> CommentRepository:
    return CommentRepository(db)


# dependency injection
def get_comment_service(
    repository: CommentRepository = Depends(get_comment_repository),
    review_repository: ReviewRepository = Depends(get_review_repository),
    notification_service: NotificationService = Depends(get_notification_service),
    db: Session = Depends(get_db),
) -> CommentService:
    return CommentService(repository, review_repository, notification_service, db)