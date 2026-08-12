from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from common.base_repository import BaseRepository
from common.page import Page
from common.pageable import Pageable
from common.sort_direction import SortDirection
from modules.notifications.models import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def find_by_recipient_id(self, recipient_id: str, pageable: Pageable) -> Page[Notification]:
        """Lấy danh sách notification theo recipient, mới nhất trước."""
        base_query = select(Notification).where(
            Notification.recipient_id == recipient_id
        )

        # Sorting
        if pageable.sort_by:
            column = getattr(Notification, pageable.sort_by, None)
            if column is not None:
                base_query = base_query.order_by(
                    column.asc()
                    if pageable.sort_direction == SortDirection.ASC
                    else column.desc()
                )
        else:
            base_query = base_query.order_by(Notification.created_at.desc())

        # Count total
        total = self.db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.recipient_id == recipient_id)
        ) or 0

        # Pagination
        offset = (pageable.page - 1) * pageable.size
        items = self.db.scalars(
            base_query.offset(offset).limit(pageable.size)
        ).all()

        return Page(items=items, total=total)

    def count_unread(self, recipient_id: str) -> int:
        """Đếm số notification chưa đọc."""
        return self.db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.recipient_id == recipient_id)
            .where(Notification.is_read == False)
        ) or 0

    def mark_all_as_read(self, recipient_id: str) -> int:
        """Đánh dấu tất cả notification của user là đã đọc. Trả về số dòng đã update."""
        result = self.db.execute(
            update(Notification)
            .where(Notification.recipient_id == recipient_id)
            .where(Notification.is_read == False)
            .values(is_read=True)
        )
        return result.rowcount
