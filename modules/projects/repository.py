from sqlalchemy.orm import Session

from common.base_repository import BaseRepository
from modules.projects.models import Project


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)
