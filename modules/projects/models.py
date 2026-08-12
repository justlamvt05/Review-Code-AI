from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, UUID as SQLUUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import BaseModel


class Project(BaseModel):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    repository_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    branch: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default="main",
    )

    owner_id: Mapped[UUID] = mapped_column(
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

    owner = relationship("User", back_populates="projects")
    reviews = relationship("Review", back_populates="project", cascade="all, delete-orphan")
