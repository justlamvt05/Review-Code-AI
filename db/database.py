from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import create_engine
from sqlalchemy import UUID as SQLUUID
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

from core.config import settings

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{settings.database_user}:"
    f"{settings.database_password}@"
    f"{settings.database_host}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class BaseModel(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


