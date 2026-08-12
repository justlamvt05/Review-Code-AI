from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):

    content: list[T]

    page: int

    size: int

    total_elements: int

    total_pages: int

    has_next: bool

    has_previous: bool
