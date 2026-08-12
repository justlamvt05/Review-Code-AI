from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from modules.projects.repository import ProjectRepository
from modules.projects.service import ProjectService


# dependency injection
def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)


# dependency injection
def get_project_service(
    repository: ProjectRepository = Depends(get_project_repository),
    db: Session = Depends(get_db),
) -> ProjectService:
    return ProjectService(repository, db)
