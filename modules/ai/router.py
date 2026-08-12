from common.responses import ApiResponse
from fastapi import APIRouter, Depends

from modules.ai.dependencies import get_ai_review_service
from modules.ai.schemas import AIReviewRequest
from modules.ai.service import AIReviewService
from modules.auth.dependencies import require_user
from modules.users.models import User

router = APIRouter(
    prefix="/ai-reviews",
    tags=["AI Reviews"],
)


@router.post("/")
async def create_ai_review(
    request: AIReviewRequest,
    current_user: User = Depends(require_user),
    service: AIReviewService = Depends(get_ai_review_service),
):
    """
    Tạo AI code review cho một file trong project.

    Flow:
    1. Đọc source code từ project files
    2. Build prompt với coding rules
    3. Gửi đến AI provider (OpenAI/Gemini/Claude)
    4. Parse response và lưu kết quả
    """
    result = await service.review_code(request, str(current_user.id))
    return ApiResponse(
        success=True,
        message="AI review completed successfully",
        data=result,
    )