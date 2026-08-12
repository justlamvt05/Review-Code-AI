from common.responses import ApiResponse
from fastapi import APIRouter, Depends, Query

from modules.auth.dependencies import require_user
from modules.search.dependencies import get_search_service
from modules.search.schemas import SearchType
from modules.search.service import SearchService
from modules.users.models import User

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/")
def search(
    q: str = Query(..., min_length=1, max_length=200, description="Từ khoá tìm kiếm"),
    type: SearchType = Query(SearchType.ALL, description="Loại tìm kiếm"),
    limit: int = Query(20, ge=1, le=100, description="Số kết quả tối đa mỗi loại"),
    offset: int = Query(0, ge=0, description="Vị trí bắt đầu"),
    current_user: User = Depends(require_user),
    service: SearchService = Depends(get_search_service),
):
    """
    Tìm kiếm tổng hợp: project, review, user.

    - `type=all` — tìm tất cả
    - `type=project` — chỉ tìm project
    - `type=review` — chỉ tìm review
    - `type=user` — chỉ tìm user
    """
    result = service.search(
        query=q,
        search_type=type,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(
        success=True,
        message="Search completed successfully",
        data=result,
    )
