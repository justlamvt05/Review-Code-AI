from sqlalchemy import func, select
from sqlalchemy.orm import Session

from common.base_repository import BaseRepository
from common.page import Page
from common.pageable import Pageable
from common.sort_direction import SortDirection
from modules.comments.models import Comment


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(Comment, db)

    def find_by_review_id(self, review_id: str, pageable: Pageable) -> Page[Comment]:
        """Lấy danh sách comment gốc (parent_id IS NULL) theo review_id."""
        base_query = (
            select(Comment)
            .where(Comment.review_id == review_id)
            .where(Comment.parent_id.is_(None))
        )

        # Sorting
        if pageable.sort_by:
            column = getattr(Comment, pageable.sort_by, None)
            if column is not None:
                base_query = base_query.order_by(
                    column.asc()
                    if pageable.sort_direction == SortDirection.ASC
                    else column.desc()
                )
        else:
            base_query = base_query.order_by(Comment.created_at.asc())

        # Count total (chỉ đếm comment gốc)
        total = self.db.scalar(
            select(func.count())
            .select_from(Comment)
            .where(Comment.review_id == review_id)
            .where(Comment.parent_id.is_(None))
        ) or 0

        # Pagination
        offset = (pageable.page - 1) * pageable.size
        items = self.db.scalars(
            base_query.offset(offset).limit(pageable.size)
        ).all()

        return Page(items=items, total=total)