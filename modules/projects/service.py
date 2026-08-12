import os
import shutil
import subprocess
import zipfile
from math import ceil
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from common.base_service import BaseService
from common.exceptions import NotFoundException, ForbiddenException, BadRequestException
from common.pageable import Pageable
from common.responses import PageResponse
from core.config import settings
from modules.projects.models import Project
from modules.projects.repository import ProjectRepository
from modules.projects.schemas import (
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectResponse,
)
from modules.users.models import User
from modules.users.role import Role

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".c", ".cpp", ".h", ".cs",
    ".rb", ".php", ".swift", ".kt",
    ".sql", ".html", ".css", ".scss",
    ".json", ".xml", ".yaml", ".yml", ".toml",
    ".md", ".txt",
}


class ProjectService(BaseService[Project]):
    def __init__(self, repository: ProjectRepository, db: Session):
        super().__init__(repository)
        self.db = db

    def create(self, request: CreateProjectRequest, owner_id: str) -> ProjectResponse:
        project = Project(
            name=request.name,
            description=request.description,
            repository_url=request.repository_url,
            branch=request.branch,
            owner_id=owner_id,
        )
        self.repository.save(project)
        self.db.commit()
        self.db.refresh(project)
        return ProjectResponse.model_validate(project)

    def get_all(self, pageable: Pageable) -> PageResponse[ProjectResponse]:
        page = self.repository.paginate(pageable)
        return PageResponse(
            content=[
                ProjectResponse.model_validate(project)
                for project in page.items
            ],
            page=pageable.page,
            size=pageable.size,
            total_elements=page.total,
            total_pages=ceil(page.total / pageable.size) if page.total > 0 else 0,
            has_next=pageable.page * pageable.size < page.total,
            has_previous=pageable.page > 1,
        )

    def get_by_id(self, project_id: str) -> ProjectResponse:
        project = self.repository.find_by_id(project_id)
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )
        return ProjectResponse.model_validate(project)

    def update(
        self,
        project_id: str,
        request: UpdateProjectRequest,
        current_user: User,
    ) -> ProjectResponse:
        project = self.repository.find_by_id(project_id)
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )

        self._check_ownership(project, current_user)

        if request.name is not None:
            project.name = request.name
        if request.description is not None:
            project.description = request.description
        if request.repository_url is not None:
            project.repository_url = request.repository_url
        if request.branch is not None:
            project.branch = request.branch

        self.db.commit()
        self.db.refresh(project)
        return ProjectResponse.model_validate(project)

    def delete_by_id(self, project_id: str, current_user: User) -> None:
        project = self.repository.find_by_id(project_id)
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )

        self._check_ownership(project, current_user)

        self.repository.delete(project)
        self.db.commit()

    # ----- Git Repository -----
    def clone_repository(self, project_id: str, current_user: User) -> dict:
        project = self.repository.find_by_id(project_id)
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )

        self._check_ownership(project, current_user)

        if not project.repository_url:
            raise BadRequestException(
                message="Project does not have a repository URL",
                error_code="MISSING_REPOSITORY_URL",
            )

        branch = project.branch or "main"
        clone_dir = Path(settings.repos_dir) / str(project.id)

        # Xoá thư mục cũ nếu tồn tại (re-clone)
        if clone_dir.exists():
            shutil.rmtree(clone_dir)

        clone_dir.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                [
                    "git", "clone",
                    "--branch", branch,
                    "--single-branch",
                    "--depth", "1",
                    project.repository_url,
                    str(clone_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.CalledProcessError as e:
            raise BadRequestException(
                message=f"Failed to clone repository: {e.stderr.strip()}",
                error_code="CLONE_FAILED",
            )
        except subprocess.TimeoutExpired:
            raise BadRequestException(
                message="Clone operation timed out (120s)",
                error_code="CLONE_TIMEOUT",
            )

        return {
            "project_id": str(project.id),
            "repository_url": project.repository_url,
            "branch": branch,
            "clone_path": str(clone_dir),
        }

    # Upload file zip
    async def upload_zip(
        self, project_id: str, file: UploadFile, current_user: User,
    ) -> dict:
        project = self.repository.find_by_id(project_id)
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )

        self._check_ownership(project, current_user)

        # Validate file type
        if not file.filename or not file.filename.lower().endswith(".zip"):
            raise BadRequestException(
                message="Only ZIP files are allowed",
                error_code="INVALID_FILE_TYPE",
            )

        # Validate file size
        max_bytes = settings.max_zip_size_mb * 1024 * 1024
        contents = await file.read()
        if len(contents) > max_bytes:
            raise BadRequestException(
                message=f"File size exceeds {settings.max_zip_size_mb}MB limit",
                error_code="FILE_TOO_LARGE",
            )

        upload_dir = Path(settings.upload_dir) / str(project.id)

        # Xoá thư mục cũ nếu tồn tại (re-upload)
        if upload_dir.exists():
            shutil.rmtree(upload_dir)

        upload_dir.mkdir(parents=True, exist_ok=True)

        # Lưu file ZIP tạm
        zip_path = upload_dir / file.filename
        with open(zip_path, "wb") as f:
            f.write(contents)

        # Giải nén
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(upload_dir)
        except zipfile.BadZipFile:
            shutil.rmtree(upload_dir)
            raise BadRequestException(
                message="Invalid or corrupted ZIP file",
                error_code="INVALID_ZIP",
            )
        finally:
            # Xoá file ZIP sau khi giải nén
            if zip_path.exists():
                os.remove(zip_path)

        # Liệt kê file đã giải nén
        extracted_files = []
        for root, _, files in os.walk(upload_dir):
            for fname in files:
                full_path = Path(root) / fname
                relative = full_path.relative_to(upload_dir)
                extracted_files.append({
                    "path": str(relative),
                    "size": full_path.stat().st_size,
                })

        return {
            "project_id": str(project.id),
            "total_files": len(extracted_files),
            "files": extracted_files,
        }


    # Upload file
    async def upload_file(
        self, project_id: str, file: UploadFile, current_user: User,
    ) -> dict:
        project = self.repository.find_by_id(project_id)
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )

        self._check_ownership(project, current_user)

        # Validate file name & extension
        if not file.filename:
            raise BadRequestException(
                message="File name is required",
                error_code="MISSING_FILE_NAME",
            )

        self._validate_file_extension(file.filename)

        # Validate file size
        max_bytes = settings.max_file_size_mb * 1024 * 1024
        contents = await file.read()
        if len(contents) > max_bytes:
            raise BadRequestException(
                message=f"File size exceeds {settings.max_file_size_mb}MB limit",
                error_code="FILE_TOO_LARGE",
            )

        upload_dir = Path(settings.upload_dir) / str(project.id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename

        with open(file_path, "wb") as f:
            f.write(contents)

        return {
            "project_id": str(project.id),
            "file_name": file.filename,
            "file_size": len(contents),
            "file_path": str(file_path.relative_to(Path(settings.upload_dir))),
        }


    # ----- Helpers -----

    @staticmethod
    def _check_ownership(project: Project, current_user: User) -> None:
        if current_user.role != Role.ROLE_ADMIN and str(project.owner_id) != str(current_user.id):
            raise ForbiddenException(
                message="You do not have permission to modify this resource",
                error_code="FORBIDDEN"
            )
    @staticmethod
    def _validate_file_extension(filename: str) -> None:
        extension = Path(filename).suffix
        if extension not in ALLOWED_EXTENSIONS:
            raise BadRequestException(
                message=f"File extension '{extension}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                error_code="INVALID_FILE_EXTENSION"
            )


