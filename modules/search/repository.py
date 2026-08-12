from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from modules.projects.models import Project
from modules.reviews.models import Review
from modules.users.models import User


class SearchRepository:
    """Repository trực tiếp query search trên nhiều bảng."""

    def __init__(self, db: Session):
        self.db = db

    def search_projects(self, keyword: str, limit: int = 20, offset: int = 0) -> tuple[list[Project], int]:
        """Tìm project theo name hoặc description."""
        pattern = f"%{keyword}%"

        base_query = select(Project).where(
            or_(
                Project.name.ilike(pattern),
                Project.description.ilike(pattern),
            )
        ).order_by(Project.created_at.desc())

        # Count
        total = self.db.scalar(
            select(func.count()).select_from(Project).where(
                or_(
                    Project.name.ilike(pattern),
                    Project.description.ilike(pattern),
                )
            )
        ) or 0

        items = self.db.scalars(
            base_query.offset(offset).limit(limit)
        ).all()

        return items, total

    def search_reviews(self, keyword: str, limit: int = 20, offset: int = 0) -> tuple[list[Review], int]:
        """Tìm review theo content."""
        pattern = f"%{keyword}%"

        base_query = select(Review).where(
            Review.content.ilike(pattern)
        ).order_by(Review.created_at.desc())

        # Count
        total = self.db.scalar(
            select(func.count()).select_from(Review).where(
                Review.content.ilike(pattern)
            )
        ) or 0

        items = self.db.scalars(
            base_query.offset(offset).limit(limit)
        ).all()

        return items, total

    def search_users(self, keyword: str, limit: int = 20, offset: int = 0) -> tuple[list[User], int]:
        """Tìm user theo email."""
        pattern = f"%{keyword}%"

        base_query = select(User).where(
            User.email.ilike(pattern)
        ).order_by(User.created_at.desc())

        # Count
        total = self.db.scalar(
            select(func.count()).select_from(User).where(
                User.email.ilike(pattern)
            )
        ) or 0

        items = self.db.scalars(
            base_query.offset(offset).limit(limit)
        ).all()

        return items, total
