from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from modules.projects.repository import ProjectRepository
from modules.projects.dependencies import get_project_repository
from modules.reviews.repository import ReviewRepository
from modules.reviews.service import ReviewService


# dependency injection
def get_review_repository(db: Session = Depends(get_db)) -> ReviewRepository:
    return ReviewRepository(db)


# dependency injection
def get_review_service(
    repository: ReviewRepository = Depends(get_review_repository),
    project_repository: ProjectRepository = Depends(get_project_repository),
    db: Session = Depends(get_db),
) -> ReviewService:
    return ReviewService(repository, project_repository, db)
