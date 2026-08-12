from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from common.exceptions.base import AppException
from common.responses.error import ErrorResponse


async def app_exception_handler(request: Request, exception: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content=ErrorResponse(
            success=False,
            message=exception.message,
            error_code=exception.error_code,
        ).model_dump(),
    )


async def validation_exception_handler(request: Request, exception: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exception.errors()
    ]

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            success=False,
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            details=details,
        ).model_dump(),
    )


async def generic_exception_handler(request: Request, exception: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
        ).model_dump(),
    )
