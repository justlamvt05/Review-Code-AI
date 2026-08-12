from common.exceptions.base import AppException


class UnauthorizedException(AppException):

    def __init__(
        self,
        message: str = "Unauthorized",
        error_code: str | None = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code,
        )
