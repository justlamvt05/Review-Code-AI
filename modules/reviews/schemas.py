from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateReviewRequest(BaseModel):
    content: str = Field(min_length=1)
    rating: int | None = Field(default=None, ge=1, le=5)
    project_id: UUID


class ReviewResponse(BaseModel):
    id: UUID
    content: str
    rating: int | None
    project_id: UUID
    reviewer_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
