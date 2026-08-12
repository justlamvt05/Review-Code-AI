from math import ceil
from typing import Generic, TypeVar, Type
from common.base_repository import BaseRepository
from common.responses import PageResponse
from common.pageable import Pageable

T = TypeVar('T')

class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository

    def find_all(self):
        return self.repository.find_all()

    def find_by_id(self, id):
        return self.repository.find_by_id(id)

    def save(self, entity):
        return self.repository.save(entity)

    def delete(self, entity):
        return self.repository.delete(entity)

    def paginate(self, pageable: Pageable) -> PageResponse[T]:
        page = self.repository.paginate(pageable)

        return PageResponse(
            content=page.items,
            page=pageable.page,
            size=pageable.size,
            total_elements=page.total,
            total_pages=ceil(page.total / pageable.size),
            has_next=pageable.page * pageable.size < page.total,
            has_previous=pageable.page > 1,
        )