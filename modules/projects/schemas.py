from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    repository_url: str | None = Field(default=None, max_length=500)
    branch: str | None = Field(default="main", max_length=100)


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    repository_url: str | None = Field(default=None, max_length=500)
    branch: str | None = Field(default=None, max_length=100)


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    repository_url: str | None
    branch: str | None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
