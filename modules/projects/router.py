from uuid import UUID

from common.pageable import Pageable
from common.responses import ApiResponse
from common.sort_direction import SortDirection
from fastapi import APIRouter, Depends, Query, UploadFile, File

from modules.auth.dependencies import require_user
from modules.projects.dependencies import get_project_service
from modules.projects.schemas import CreateProjectRequest, UpdateProjectRequest
from modules.projects.service import ProjectService
from modules.users.models import User

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
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
def get_projects(
    current_user: User = Depends(require_user),
    pageable: Pageable = Depends(get_pageable),
    service: ProjectService = Depends(get_project_service),
):
    page = service.get_all(pageable)
    return ApiResponse(
        success=True,
        message="Projects fetched successfully",
        data=page,
    )


@router.get("/{project_id}")
def get_project(
    project_id: UUID,
    current_user: User = Depends(require_user),
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_by_id(str(project_id))
    return ApiResponse(
        success=True,
        message="Project fetched successfully",
        data=project,
    )


@router.post("/")
def create_project(
    request: CreateProjectRequest,
    current_user: User = Depends(require_user),
    service: ProjectService = Depends(get_project_service),
):
    project = service.create(request, str(current_user.id))
    return ApiResponse(
        success=True,
        message="Project created successfully",
        data=project,
    )


@router.put("/{project_id}")
def update_project(
    project_id: UUID,
    request: UpdateProjectRequest,
    current_user: User = Depends(require_user),
    service: ProjectService = Depends(get_project_service),
):
    project = service.update(str(project_id), request, current_user)
    return ApiResponse(
        success=True,
        message="Project updated successfully",
        data=project,
    )


@router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    current_user: User = Depends(require_user),
    service: ProjectService = Depends(get_project_service),
):
    service.delete_by_id(str(project_id), current_user)
    return ApiResponse(
        success=True,
        message="Project deleted successfully",
    )


# ----- Git Repository -----

@router.post("/{project_id}/clone")
def clone_repository(
    project_id: UUID,
    current_user: User = Depends(require_user),
    service: ProjectService = Depends(get_project_service),
):
    result = service.clone_repository(str(project_id), current_user)
    return ApiResponse(
        success=True,
        message="Repository cloned successfully",
        data=result,
    )


# ----- Upload Source Code -----

@router.post("/{project_id}/upload/zip")
async def upload_zip(
    project_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(require_user),
    service: ProjectService = Depends(get_project_service),
):
    result = await service.upload_zip(str(project_id), file, current_user)
    return ApiResponse(
        success=True,
        message="ZIP file uploaded and extracted successfully",
        data=result,
    )


@router.post("/{project_id}/upload/file")
async def upload_file(
    project_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(require_user),
    service: ProjectService = Depends(get_project_service),
):
    result = await service.upload_file(str(project_id), file, current_user)
    return ApiResponse(
        success=True,
        message="File uploaded successfully",
        data=result,
    )
