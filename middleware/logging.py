import time

from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware

from core.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(

        self,

        request: Request,

        call_next

    ):

        start = time.time()

        response = await call_next(request)

        process = time.time() - start

        logger.info(

            "%s %s %s %.3fs",

            request.method,

            request.url.path,

            response.status_code,

            process

        )

        return response