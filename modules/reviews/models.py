from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UUID as SQLUUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import BaseModel


class Review(BaseModel):
    __tablename__ = "reviews"

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    project_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )

    reviewer_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    project = relationship("Project", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
    comments = relationship("Comment", back_populates="review", cascade="all, delete-orphan")