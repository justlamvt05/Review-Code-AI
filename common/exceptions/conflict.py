from common.exceptions.base import AppException


class ConflictException(AppException):

    def __init__(
        self,
        message: str = "Resource already exists",
        error_code: str | None = None,
    ):
        super().__init__(
            message=message,
            status_code=409,
            error_code=error_code,
        )
