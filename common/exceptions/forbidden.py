from common.exceptions.base import AppException


class ForbiddenException(AppException):

    def __init__(
        self,
        message: str = "Forbidden",
        error_code: str | None = None,
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code=error_code,
        )
