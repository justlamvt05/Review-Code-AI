from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ----- Request -----

class AIReviewRequest(BaseModel):
    """Request body để tạo AI review."""
    project_id: UUID
    file_path: str = Field(
        ...,
        min_length=1,
        description="Đường dẫn file cần review (relative path trong project)",
        examples=["src/main.py", "app/services/user_service.java"],
    )
    language: str = Field(
        default="general",
        description="Ngôn ngữ lập trình",
        examples=["python", "javascript", "java"],
    )
    custom_rules: list[str] = Field(
        default_factory=list,
        description="Custom coding rules bổ sung",
        examples=[["No global variables", "Use dataclasses instead of dicts"]],
    )
    provider: str | None = Field(
        default=None,
        description="Override AI provider (openai/gemini/claude). Nếu None sẽ dùng default từ config",
    )


# ----- Response -----

class ReviewIssueResponse(BaseModel):
    severity: str
    line: int | None = None
    title: str
    description: str
    suggestion: str = ""


class AIReviewResponse(BaseModel):
    """Response trả về cho client."""
    id: UUID
    project_id: UUID
    file_path: str
    language: str
    provider: str
    summary: str
    rating: int
    issues: list[ReviewIssueResponse] = []
    strengths: list[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)