from uuid import UUID

from common.pageable import Pageable
from common.responses import ApiResponse
from common.sort_direction import SortDirection
from fastapi import APIRouter, Depends, Query

from modules.auth.dependencies import require_user
from modules.reviews.dependencies import get_review_service
from modules.reviews.schemas import CreateReviewRequest
from modules.reviews.service import ReviewService
from modules.users.models import User

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
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
def create_review(
    request: CreateReviewRequest,
    current_user: User = Depends(require_user),
    service: ReviewService = Depends(get_review_service),
):
    review = service.create(request, str(current_user.id))
    return ApiResponse(
        success=True,
        message="Review created successfully",
        data=review,
    )


@router.get("/")
def get_reviews(
    current_user: User = Depends(require_user),
    pageable: Pageable = Depends(get_pageable),
    service: ReviewService = Depends(get_review_service),
):
    page = service.get_all(pageable)
    return ApiResponse(
        success=True,
        message="Reviews fetched successfully",
        data=page,
    )


@router.get("/project/{project_id}")
def get_reviews_by_project(
    project_id: UUID,
    current_user: User = Depends(require_user),
    pageable: Pageable = Depends(get_pageable),
    service: ReviewService = Depends(get_review_service),
):
    page = service.get_by_project_id(str(project_id), pageable)
    return ApiResponse(
        success=True,
        message="Reviews fetched successfully",
        data=page,
    )


@router.get("/{review_id}")
def get_review(
    review_id: UUID,
    current_user: User = Depends(require_user),
    service: ReviewService = Depends(get_review_service),
):
    review = service.get_by_id(str(review_id))
    return ApiResponse(
        success=True,
        message="Review fetched successfully",
        data=review,
    )


@router.delete("/{review_id}")
def delete_review(
    review_id: UUID,
    current_user: User = Depends(require_user),
    service: ReviewService = Depends(get_review_service),
):
    service.delete_by_id(str(review_id), current_user)
    return ApiResponse(
        success=True,
        message="Review deleted successfully",
    )
