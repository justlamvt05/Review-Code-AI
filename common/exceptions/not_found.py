from common.exceptions.base import AppException


class NotFoundException(AppException):

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str | None = None,
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code=error_code,
        )
