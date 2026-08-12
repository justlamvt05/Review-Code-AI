from typing import Generic, TypeVar, Type

from sqlalchemy import func, select, exists
from sqlalchemy.orm import Session

from common.page import Page
from common.pageable import Pageable
from common.sort_direction import SortDirection

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def find_all(self):
        statement = select(self.model)
        return self.db.scalar(statement).all()

    def find_by_id(self, entity_id):
        return self.db.get(self.model, entity_id)

    def save(self, entity: T):
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T):
        self.db.delete(entity)
        return entity

    def count(self):
        statement = select(
            func.count()
        ).select_from(self.model)
        return self.db.scalar(statement)

    def exists_by_id(self, entity_id):
        statement = select(
            exists().where(self.model.id == entity_id)
        )
        return self.db.scalar(statement)

    def paginate(self, pageable: Pageable) -> Page[T]:
        statement = select(self.model)

        if pageable.sort_by:
            column = getattr(self.model, pageable.sort_by, None)

            if column is not None:
                statement = statement.order_by(
                    column.asc()
                    if pageable.sort_direction == SortDirection.ASC
                    else column.desc()
                )

        total = self.db.scalar(
            select(func.count()).select_from(self.model)
        ) or 0

        offset = (pageable.page - 1) * pageable.size

        items = self.db.scalars(
            statement.offset(offset).limit(pageable.size)
        ).all()

        return Page(
            items=items,
            total=total
        )