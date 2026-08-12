from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from modules.projects.repository import ProjectRepository
from modules.projects.dependencies import get_project_repository
from modules.reviews.repository import ReviewRepository
from modules.reviews.dependencies import get_review_repository
from modules.ai.service import AIReviewService


def get_ai_review_service(
    review_repository: ReviewRepository = Depends(get_review_repository),
    project_repository: ProjectRepository = Depends(get_project_repository),
    db: Session = Depends(get_db),
) -> AIReviewService:
    return AIReviewService(review_repository, project_repository, db)