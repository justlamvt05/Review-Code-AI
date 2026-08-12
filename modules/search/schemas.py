import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SearchType(str, enum.Enum):
    PROJECT = "project"
    REVIEW = "review"
    USER = "user"
    ALL = "all"


# ----- Individual Search Results -----

class ProjectSearchResult(BaseModel):
    id: UUID
    name: str
    description: str | None
    repository_url: str | None
    owner_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewSearchResult(BaseModel):
    id: UUID
    content: str
    rating: int | None
    project_id: UUID
    reviewer_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSearchResult(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----- Combined Search Response -----

class SearchResponse(BaseModel):
    """Response cho search tổng hợp."""
    query: str
    type: SearchType
    projects: list[ProjectSearchResult] = []
    reviews: list[ReviewSearchResult] = []
    users: list[UserSearchResult] = []
    total_results: int = 0
