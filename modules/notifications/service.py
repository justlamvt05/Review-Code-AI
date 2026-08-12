from math import ceil

from sqlalchemy.orm import Session

from common.exceptions import NotFoundException
from common.pageable import Pageable
from common.responses import PageResponse
from modules.notifications.email_service import EmailService
from modules.notifications.models import Notification, NotificationType
from modules.notifications.repository import NotificationRepository
from modules.notifications.schemas import NotificationResponse, UnreadCountResponse
from modules.users.repository import UserRepository


class NotificationService:
    def __init__(
        self,
        repository: NotificationRepository,
        user_repository: UserRepository,
        db: Session,
    ):
        self.repository = repository
        self.user_repository = user_repository
        self.db = db

    # ----- In-App Notification -----

    def create_notification(
        self,
        recipient_id: str,
        sender_id: str | None,
        notification_type: NotificationType,
        title: str,
        message: str,
        reference_id: str | None = None,
    ) -> Notification:
        """Tạo in-app notification và lưu vào DB."""
        notification = Notification(
            recipient_id=recipient_id,
            sender_id=sender_id,
            type=notification_type,
            title=title,
            message=message,
            reference_id=reference_id,
        )
        self.repository.save(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_my_notifications(
        self, user_id: str, pageable: Pageable,
    ) -> PageResponse[NotificationResponse]:
        """Lấy danh sách notification của user hiện tại."""
        page = self.repository.find_by_recipient_id(user_id, pageable)
        return PageResponse(
            content=[
                NotificationResponse.model_validate(n)
                for n in page.items
            ],
            page=pageable.page,
            size=pageable.size,
            total_elements=page.total,
            total_pages=ceil(page.total / pageable.size) if page.total > 0 else 0,
            has_next=pageable.page * pageable.size < page.total,
            has_previous=pageable.page > 1,
        )

    def get_unread_count(self, user_id: str) -> UnreadCountResponse:
        """Đếm số notification chưa đọc."""
        count = self.repository.count_unread(user_id)
        return UnreadCountResponse(count=count)

    def mark_as_read(self, notification_id: str, user_id: str) -> NotificationResponse:
        """Đánh dấu 1 notification đã đọc."""
        notification = self.repository.find_by_id(notification_id)
        if not notification:
            raise NotFoundException(
                message="Notification not found",
                error_code="NOTIFICATION_NOT_FOUND",
            )

        # Chỉ recipient mới được đánh dấu đọc
        if str(notification.recipient_id) != user_id:
            raise NotFoundException(
                message="Notification not found",
                error_code="NOTIFICATION_NOT_FOUND",
            )

        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return NotificationResponse.model_validate(notification)

    def mark_all_as_read(self, user_id: str) -> dict:
        """Đánh dấu tất cả notification đã đọc."""
        count = self.repository.mark_all_as_read(user_id)
        self.db.commit()
        return {"marked_count": count}

    # ----- Email Notification -----

    def notify_new_comment(
        self,
        review_owner_id: str,
        commenter_id: str,
        review_content: str,
        comment_content: str,
        review_id: str,
    ) -> None:
        """
        Gửi notification khi có comment mới trên review.
        - Tạo in-app notification
        - Gửi email (nếu enabled)
        """
        # Không gửi notification cho chính mình
        if review_owner_id == commenter_id:
            return

        commenter = self.user_repository.find_by_id(commenter_id)
        recipient = self.user_repository.find_by_id(review_owner_id)

        if not commenter or not recipient:
            return

        # 1. In-App
        self.create_notification(
            recipient_id=review_owner_id,
            sender_id=commenter_id,
            notification_type=NotificationType.COMMENT_ADDED,
            title="New comment on your review",
            message=f"{commenter.email} commented: {comment_content[:100]}",
            reference_id=review_id,
        )

        # 2. Email
        html = EmailService.build_comment_notification_html(
            commenter_name=commenter.email,
            review_content=review_content,
            comment_content=comment_content,
        )
        EmailService.send_email(
            to_email=recipient.email,
            subject="💬 New comment on your review — ReviewCodeWeb",
            html_body=html,
        )

    def notify_reply(
        self,
        comment_owner_id: str,
        replier_id: str,
        original_comment: str,
        reply_content: str,
        review_id: str,
    ) -> None:
        """
        Gửi notification khi có reply.
        - Tạo in-app notification
        - Gửi email (nếu enabled)
        """
        # Không gửi notification cho chính mình
        if comment_owner_id == replier_id:
            return

        replier = self.user_repository.find_by_id(replier_id)
        recipient = self.user_repository.find_by_id(comment_owner_id)

        if not replier or not recipient:
            return

        # 1. In-App
        self.create_notification(
            recipient_id=comment_owner_id,
            sender_id=replier_id,
            notification_type=NotificationType.COMMENT_REPLIED,
            title="New reply to your comment",
            message=f"{replier.email} replied: {reply_content[:100]}",
            reference_id=review_id,
        )

        # 2. Email
        html = EmailService.build_reply_notification_html(
            replier_name=replier.email,
            original_comment=original_comment,
            reply_content=reply_content,
        )
        EmailService.send_email(
            to_email=recipient.email,
            subject="↩️ New reply to your comment — ReviewCodeWeb",
            html_body=html,
        )
