from math import ceil

from sqlalchemy.orm import Session

from common.base_service import BaseService
from common.exceptions import NotFoundException, ForbiddenException
from common.pageable import Pageable
from common.responses import PageResponse
from modules.comments.models import Comment
from modules.comments.repository import CommentRepository
from modules.comments.schemas import (
    CreateCommentRequest,
    ReplyCommentRequest,
    CommentResponse,
    CommentWithRepliesResponse,
)
from modules.notifications.service import NotificationService
from modules.reviews.repository import ReviewRepository
from modules.users.models import User
from modules.users.role import Role


class CommentService(BaseService[Comment]):
    def __init__(
        self,
        repository: CommentRepository,
        review_repository: ReviewRepository,
        notification_service: NotificationService,
        db: Session,
    ):
        super().__init__(repository)
        self.review_repository = review_repository
        self.notification_service = notification_service
        self.db = db

    def create(self, request: CreateCommentRequest, author_id: str) -> CommentResponse:
        """Tạo comment mới cho review."""
        # Validate review tồn tại
        review = self.review_repository.find_by_id(str(request.review_id))
        if not review:
            raise NotFoundException(
                message="Review not found",
                error_code="REVIEW_NOT_FOUND",
            )

        comment = Comment(
            content=request.content,
            review_id=str(request.review_id),
            author_id=author_id,
        )
        self.repository.save(comment)
        self.db.commit()
        self.db.refresh(comment)

        # Gửi notification cho review owner
        self.notification_service.notify_new_comment(
            review_owner_id=str(review.reviewer_id),
            commenter_id=author_id,
            review_content=review.content,
            comment_content=request.content,
            review_id=str(review.id),
        )

        return CommentResponse.model_validate(comment)

    def reply(
        self,
        parent_comment_id: str,
        request: ReplyCommentRequest,
        author_id: str,
    ) -> CommentResponse:
        """Reply vào 1 comment đã tồn tại."""
        # Validate parent comment tồn tại
        parent = self.repository.find_by_id(parent_comment_id)
        if not parent:
            raise NotFoundException(
                message="Parent comment not found",
                error_code="COMMENT_NOT_FOUND",
            )

        # Chỉ cho reply 1 cấp (nếu parent đã là reply → không cho reply tiếp)
        if parent.parent_id is not None:
            raise ForbiddenException(
                message="Cannot reply to a reply. Only top-level comments can be replied to",
                error_code="NESTED_REPLY_NOT_ALLOWED",
            )

        reply_comment = Comment(
            content=request.content,
            review_id=str(parent.review_id),
            author_id=author_id,
            parent_id=parent_comment_id,
        )
        self.repository.save(reply_comment)
        self.db.commit()
        self.db.refresh(reply_comment)

        # Gửi notification cho comment owner
        self.notification_service.notify_reply(
            comment_owner_id=str(parent.author_id),
            replier_id=author_id,
            original_comment=parent.content,
            reply_content=request.content,
            review_id=str(parent.review_id),
        )

        return CommentResponse.model_validate(reply_comment)

    def get_by_review_id(
        self, review_id: str, pageable: Pageable,
    ) -> PageResponse[CommentWithRepliesResponse]:
        """Lấy danh sách comment gốc (kèm replies) theo review_id."""
        # Validate review tồn tại
        review = self.review_repository.find_by_id(review_id)
        if not review:
            raise NotFoundException(
                message="Review not found",
                error_code="REVIEW_NOT_FOUND",
            )

        page = self.repository.find_by_review_id(review_id, pageable)
        return PageResponse(
            content=[
                CommentWithRepliesResponse.model_validate(comment)
                for comment in page.items
            ],
            page=pageable.page,
            size=pageable.size,
            total_elements=page.total,
            total_pages=ceil(page.total / pageable.size) if page.total > 0 else 0,
            has_next=pageable.page * pageable.size < page.total,
            has_previous=pageable.page > 1,
        )

    def delete_by_id(self, comment_id: str, current_user: User) -> None:
        """Xoá comment (chỉ owner hoặc admin)."""
        comment = self.repository.find_by_id(comment_id)
        if not comment:
            raise NotFoundException(
                message="Comment not found",
                error_code="COMMENT_NOT_FOUND",
            )

        self._check_ownership(comment, current_user)

        self.repository.delete(comment)
        self.db.commit()

    @staticmethod
    def _check_ownership(comment: Comment, current_user: User) -> None:
        if current_user.role != Role.ROLE_ADMIN and str(comment.author_id) != str(current_user.id):
            raise ForbiddenException(
                message="You do not have permission to delete this comment",
                error_code="FORBIDDEN",
            )