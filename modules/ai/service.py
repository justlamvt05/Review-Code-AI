import json
from pathlib import Path

from sqlalchemy.orm import Session

from common.exceptions import NotFoundException, BadRequestException
from core.config import settings
from modules.ai.prompt_builder import PromptBuilder
from modules.ai.providers.base import BaseAIProvider, create_ai_provider
from modules.ai.response_parser import ResponseParser, AIReviewResult
from modules.ai.schemas import AIReviewRequest, AIReviewResponse, ReviewIssueResponse
from modules.projects.repository import ProjectRepository
from modules.reviews.models import Review
from modules.reviews.repository import ReviewRepository


class AIReviewService:
    """
    Orchestrator chính cho AI Code Review.
    Flow: Read Code → Build Prompt → Call AI → Parse Response → Save Review
    """

    def __init__(
        self,
        review_repository: ReviewRepository,
        project_repository: ProjectRepository,
        db: Session,
    ):
        self.review_repository = review_repository
        self.project_repository = project_repository
        self.db = db

    async def review_code(
        self,
        request: AIReviewRequest,
        reviewer_id: str,
    ) -> AIReviewResponse:
        """
        Full flow AI review:
        1. Validate project tồn tại
        2. Đọc source code từ file
        3. Build prompt
        4. Gọi AI provider
        5. Parse response
        6. Lưu kết quả vào DB
        7. Trả response cho client
        """

        # 1. Validate project
        project = self.project_repository.find_by_id(str(request.project_id))
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )

        # 2. Đọc source code
        source_code = self._read_source_code(
            project_id=str(request.project_id),
            file_path=request.file_path,
        )

        # 3. Build prompt
        prompt = (
            PromptBuilder(
                source_code=source_code,
                language=request.language,
                file_name=request.file_path,
            )
            .add_rules(request.custom_rules)
            .build()
        )

        # 4. Gọi AI
        provider: BaseAIProvider = create_ai_provider(request.provider)
        raw_response = await provider.generate(prompt)

        # 5. Parse response
        result: AIReviewResult = ResponseParser.parse(raw_response)

        # 6. Save vào DB
        review = Review(
            content=json.dumps({
                "summary": result.summary,
                "issues": [
                    {
                        "severity": issue.severity,
                        "line": issue.line,
                        "title": issue.title,
                        "description": issue.description,
                        "suggestion": issue.suggestion,
                    }
                    for issue in result.issues
                ],
                "strengths": result.strengths,
                "provider": provider.provider_name,
                "file_path": request.file_path,
                "language": request.language,
            }),
            rating=result.rating,
            project_id=str(request.project_id),
            reviewer_id=reviewer_id,
        )
        self.review_repository.save(review)
        self.db.commit()
        self.db.refresh(review)

        # 7. Build response
        return AIReviewResponse(
            id=review.id,
            project_id=review.project_id,
            file_path=request.file_path,
            language=request.language,
            provider=provider.provider_name,
            summary=result.summary,
            rating=result.rating,
            issues=[
                ReviewIssueResponse(
                    severity=issue.severity,
                    line=issue.line,
                    title=issue.title,
                    description=issue.description,
                    suggestion=issue.suggestion,
                )
                for issue in result.issues
            ],
            strengths=result.strengths,
            created_at=review.created_at,
        )

    # ----- Helpers -----

    @staticmethod
    def _read_source_code(project_id: str, file_path: str) -> str:
        """
        Đọc source code file từ uploads/ hoặc repos/.
        Tìm ở uploads trước, nếu không có thì tìm ở repos.
        """
        possible_dirs = [
            Path(settings.upload_dir) / project_id,
            Path(settings.repos_dir) / project_id,
        ]

        for base_dir in possible_dirs:
            full_path = base_dir / file_path
            if full_path.is_file():
                try:
                    return full_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    raise BadRequestException(
                        message=f"Cannot read file (binary or unsupported encoding): {file_path}",
                        error_code="UNREADABLE_FILE",
                    )

        raise NotFoundException(
            message=f"Source file not found: {file_path}",
            error_code="FILE_NOT_FOUND",
        )