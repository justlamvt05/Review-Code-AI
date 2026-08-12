from fastapi import Depends
from sqlalchemy.orm import Session

from db.database import get_db
from modules.search.repository import SearchRepository
from modules.search.service import SearchService


# dependency injection
def get_search_repository(db: Session = Depends(get_db)) -> SearchRepository:
    return SearchRepository(db)


# dependency injection
def get_search_service(
    repository: SearchRepository = Depends(get_search_repository),
) -> SearchService:
    return SearchService(repository)
