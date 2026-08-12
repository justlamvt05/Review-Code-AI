from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ----- Request -----

class CreateCommentRequest(BaseModel):
    """Request body để tạo comment mới cho review."""
    content: str = Field(min_length=1, max_length=5000)
    review_id: UUID


class ReplyCommentRequest(BaseModel):
    """Request body để reply 1 comment."""
    content: str = Field(min_length=1, max_length=5000)


# ----- Response -----

class CommentResponse(BaseModel):
    """Response trả về cho 1 comment (không gồm replies)."""
    id: UUID
    content: str
    review_id: UUID
    author_id: UUID
    parent_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentWithRepliesResponse(BaseModel):
    """Response trả về cho 1 comment gốc kèm danh sách replies."""
    id: UUID
    content: str
    review_id: UUID
    author_id: UUID
    parent_id: UUID | None
    created_at: datetime
    updated_at: datetime
    replies: list[CommentResponse] = []

    model_config = ConfigDict(from_attributes=True)