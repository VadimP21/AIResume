from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

import structlog

logger = structlog.get_logger()


class AppException(Exception):
    def __init__(self, message: str):
        self.message = message

class NotFoundException(AppException):
    pass

async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    logger.error(
        "application_error",
        message=exc.message,
        request_id=request.state.request_id,
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message,
        },
    )