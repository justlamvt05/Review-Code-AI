from math import ceil

from sqlalchemy.orm import Session

from core.logger import logger
from common.base_service import BaseService
from common.exceptions import NotFoundException
from common.responses import PageResponse
from common.pageable import Pageable
from modules.users.models import User
from modules.users.repository import UserRepository
from modules.users.schemas import UserResponse


class UserService(BaseService[User]):
    def __init__(self, repository: UserRepository, db: Session):
        super().__init__(repository)
        self.db = db

    def paginate(self, pageable: Pageable) -> PageResponse[UserResponse]:
        page = self.repository.paginate(pageable)

        logger.info("Total:" + str(page.total))
        return PageResponse(
            content=[
                UserResponse.model_validate(user)
                for user in page.items
            ],
            page=pageable.page,
            size=pageable.size,
            total_elements=page.total,
            total_pages=ceil(page.total / pageable.size),
            has_next=pageable.page * pageable.size < page.total,
            has_previous=pageable.page > 1,
        )

    def get_by_id(self, user_id: str) -> UserResponse:
        user = self.repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(
                message="User not found",
                error_code="USER_NOT_FOUND",
            )
        return UserResponse.model_validate(user)

    def delete_by_id(self, user_id: str) -> None:
        user = self.repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(
                message="User not found",
                error_code="USER_NOT_FOUND",
            )
        self.repository.delete(user)
        self.db.commit()
