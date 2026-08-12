from uuid import UUID

from common.pageable import Pageable
from common.responses import ApiResponse
from common.sort_direction import SortDirection
from fastapi import APIRouter, Depends, Query

from modules.auth.dependencies import require_user
from modules.notifications.dependencies import get_notification_service
from modules.notifications.service import NotificationService
from modules.users.models import User

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def get_pageable(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str | None = Query(None),
    sort_direction: SortDirection = Query(SortDirection.DESC),
) -> Pageable:
    return Pageable(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )


@router.get("/")
def get_my_notifications(
    current_user: User = Depends(require_user),
    pageable: Pageable = Depends(get_pageable),
    service: NotificationService = Depends(get_notification_service),
):
    """Lấy danh sách notification của user hiện tại."""
    page = service.get_my_notifications(str(current_user.id), pageable)
    return ApiResponse(
        success=True,
        message="Notifications fetched successfully",
        data=page,
    )


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(require_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Đếm số notification chưa đọc."""
    result = service.get_unread_count(str(current_user.id))
    return ApiResponse(
        success=True,
        message="Unread count fetched successfully",
        data=result,
    )


@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: UUID,
    current_user: User = Depends(require_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Đánh dấu 1 notification đã đọc."""
    notification = service.mark_as_read(str(notification_id), str(current_user.id))
    return ApiResponse(
        success=True,
        message="Notification marked as read",
        data=notification,
    )


@router.patch("/read-all")
def mark_all_as_read(
    current_user: User = Depends(require_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Đánh dấu tất cả notification đã đọc."""
    result = service.mark_all_as_read(str(current_user.id))
    return ApiResponse(
        success=True,
        message="All notifications marked as read",
        data=result,
    )
