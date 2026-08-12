from math import ceil

from sqlalchemy.orm import Session

from common.base_service import BaseService
from common.exceptions import NotFoundException, ForbiddenException
from common.pageable import Pageable
from common.responses import PageResponse
from modules.projects.repository import ProjectRepository
from modules.reviews.models import Review
from modules.reviews.repository import ReviewRepository
from modules.reviews.schemas import CreateReviewRequest, ReviewResponse
from modules.users.models import User
from modules.users.role import Role


class ReviewService(BaseService[Review]):
    def __init__(
        self,
        repository: ReviewRepository,
        project_repository: ProjectRepository,
        db: Session,
    ):
        super().__init__(repository)
        self.project_repository = project_repository
        self.db = db

    def create(self, request: CreateReviewRequest, reviewer_id: str) -> ReviewResponse:
        project = self.project_repository.find_by_id(str(request.project_id))
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )

        review = Review(
            content=request.content,
            rating=request.rating,
            project_id=str(request.project_id),
            reviewer_id=reviewer_id,
        )
        self.repository.save(review)
        self.db.commit()
        self.db.refresh(review)
        return ReviewResponse.model_validate(review)

    def get_by_id(self, review_id: str) -> ReviewResponse:
        review = self.repository.find_by_id(review_id)
        if not review:
            raise NotFoundException(
                message="Review not found",
                error_code="REVIEW_NOT_FOUND",
            )
        return ReviewResponse.model_validate(review)

    def get_by_project_id(
        self, project_id: str, pageable: Pageable,
    ) -> PageResponse[ReviewResponse]:
        # Kiểm tra project tồn tại
        project = self.project_repository.find_by_id(project_id)
        if not project:
            raise NotFoundException(
                message="Project not found",
                error_code="PROJECT_NOT_FOUND",
            )

        page = self.repository.find_by_project_id(project_id, pageable)
        return PageResponse(
            content=[
                ReviewResponse.model_validate(review)
                for review in page.items
            ],
            page=pageable.page,
            size=pageable.size,
            total_elements=page.total,
            total_pages=ceil(page.total / pageable.size) if page.total > 0 else 0,
            has_next=pageable.page * pageable.size < page.total,
            has_previous=pageable.page > 1,
        )

    def get_all(self, pageable: Pageable) -> PageResponse[ReviewResponse]:
        page = self.repository.paginate(pageable)
        return PageResponse(
            content=[
                ReviewResponse.model_validate(review)
                for review in page.items
            ],
            page=pageable.page,
            size=pageable.size,
            total_elements=page.total,
            total_pages=ceil(page.total / pageable.size) if page.total > 0 else 0,
            has_next=pageable.page * pageable.size < page.total,
            has_previous=pageable.page > 1,
        )

    def delete_by_id(self, review_id: str, current_user: User) -> None:
        review = self.repository.find_by_id(review_id)
        if not review:
            raise NotFoundException(
                message="Review not found",
                error_code="REVIEW_NOT_FOUND",
            )

        self._check_ownership(review, current_user)

        self.repository.delete(review)
        self.db.commit()

    @staticmethod
    def _check_ownership(review: Review, current_user: User) -> None:
        if current_user.role != Role.ROLE_ADMIN and str(review.reviewer_id) != str(current_user.id):
            raise ForbiddenException(
                message="You do not have permission to modify this resource",
                error_code="FORBIDDEN",
            )
