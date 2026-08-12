from sqlalchemy import func, select
from sqlalchemy.orm import Session

from common.base_repository import BaseRepository
from common.page import Page
from common.pageable import Pageable
from common.sort_direction import SortDirection
from modules.reviews.models import Review


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def find_by_project_id(self, project_id: str, pageable: Pageable) -> Page[Review]:
        base_query = select(Review).where(Review.project_id == project_id)

        # Sorting
        if pageable.sort_by:
            column = getattr(Review, pageable.sort_by, None)
            if column is not None:
                base_query = base_query.order_by(
                    column.asc()
                    if pageable.sort_direction == SortDirection.ASC
                    else column.desc()
                )
        else:
            # Mặc định sắp xếp theo created_at mới nhất
            base_query = base_query.order_by(Review.created_at.desc())

        # Count total
        total = self.db.scalar(
            select(func.count()).select_from(Review).where(Review.project_id == project_id)
        ) or 0

        # Pagination
        offset = (pageable.page - 1) * pageable.size
        items = self.db.scalars(
            base_query.offset(offset).limit(pageable.size)
        ).all()

        return Page(items=items, total=total)
