from uuid import UUID

from common.pageable import Pageable
from common.responses import ApiResponse
from common.sort_direction import SortDirection
from fastapi import APIRouter, Depends, Query

from modules.auth.dependencies import require_admin
from modules.users.dependencies import get_user_service
from modules.users.models import User
from modules.users.service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
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


@router.get("/")
def get_users(
    current_user: User = Depends(require_admin),
    pageable: Pageable = Depends(get_pageable),
    service: UserService = Depends(get_user_service),
):
    page = service.paginate(pageable)
    return ApiResponse(
        success=True,
        message="Users fetched successfully",
        data=page,
    )


@router.get("/{user_id}")
def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
):
    user = service.get_by_id(str(user_id))
    return ApiResponse(
        success=True,
        message="User fetched successfully",
        data=user,
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
):
    service.delete_by_id(str(user_id))
    return ApiResponse(
        success=True,
        message="User deleted successfully",
    )