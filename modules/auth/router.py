from fastapi import APIRouter, Depends

from common.responses import ApiResponse
from modules.auth.dependencies import get_auth_service, get_current_user
from modules.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from modules.auth.service import AuthService
from modules.users.models import User

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
def register(

    request: RegisterRequest,
    service: AuthService = Depends(get_auth_service),

):
    user = service.register(request)
    return ApiResponse(
        success=True,
        message="User registered successfully",
        data=user,
    )


@router.post("/login")
def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    tokens = service.login(request)
    return ApiResponse(
        success=True,
        message="Login successful",
        data=tokens,
    )


@router.post("/refresh")
def refresh(
    request: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
):
    tokens = service.refresh(request)
    return ApiResponse(
        success=True,
        message="Token refreshed successfully",
        data=tokens,
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(
        success=True,
        message="Logged out successfully",
    )


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    user = service.get_me(str(current_user.id))
    return ApiResponse(
        success=True,
        message="User retrieved successfully",
        data=user,
    )
