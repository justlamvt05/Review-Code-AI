from common.sort_direction import SortDirection
from pydantic import BaseModel, Field


class Pageable(BaseModel):

    page: int = Field(default=1, ge=1)

    size: int = Field(default=10, ge=1, le=100)

    sort_by: str | None = None

    sort_direction: SortDirection = SortDirection.ASC