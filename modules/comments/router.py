from uuid import UUID

from common.pageable import Pageable
from common.responses import ApiResponse
from common.sort_direction import SortDirection
from fastapi import APIRouter, Depends, Query

from modules.auth.dependencies import require_user
from modules.comments.dependencies import get_comment_service
from modules.comments.schemas import CreateCommentRequest, ReplyCommentRequest
from modules.comments.service import CommentService
from modules.users.models import User

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


def get_pageable(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: str | None = Query(None),
    sort_direction: SortDirection = Query(SortDirection.ASC),
) -> Pageable:
    return Pageable(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )


@router.post("/")
def create_comment(
    request: CreateCommentRequest,
    current_user: User = Depends(require_user),
    service: CommentService = Depends(get_comment_service),
):
    """Tạo comment mới cho review."""
    comment = service.create(request, str(current_user.id))
    return ApiResponse(
        success=True,
        message="Comment created successfully",
        data=comment,
    )


@router.post("/{comment_id}/reply")
def reply_comment(
    comment_id: UUID,
    request: ReplyCommentRequest,
    current_user: User = Depends(require_user),
    service: CommentService = Depends(get_comment_service),
):
    """Reply vào 1 comment đã tồn tại."""
    comment = service.reply(str(comment_id), request, str(current_user.id))
    return ApiResponse(
        success=True,
        message="Reply created successfully",
        data=comment,
    )


@router.get("/review/{review_id}")
def get_comments_by_review(
    review_id: UUID,
    current_user: User = Depends(require_user),
    pageable: Pageable = Depends(get_pageable),
    service: CommentService = Depends(get_comment_service),
):
    """Lấy danh sách comment (kèm replies) theo review."""
    page = service.get_by_review_id(str(review_id), pageable)
    return ApiResponse(
        success=True,
        message="Comments fetched successfully",
        data=page,
    )


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(require_user),
    service: CommentService = Depends(get_comment_service),
):
    """Xoá comment (chỉ owner hoặc admin)."""
    service.delete_by_id(str(comment_id), current_user)
    return ApiResponse(
        success=True,
        message="Comment deleted successfully",
    )