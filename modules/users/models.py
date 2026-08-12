
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, UUID as SQLUUID, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import BaseModel
from modules.users.role import Role


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="role_enum"),
        nullable=False
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

    projects = relationship("Project", back_populates="owner")
    reviews = relationship("Review", back_populates="reviewer")
    comments = relationship("Comment", back_populates="author")
