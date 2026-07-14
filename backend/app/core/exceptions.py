"""Содержит компоненты модуля exceptions."""

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

logger = structlog.get_logger()


class AppException(Exception):
    """Представляет сущность AppException."""

    def __init__(self, message: str):
        """Инициализирует экземпляр."""
        self.message = message


class NotFoundException(AppException):
    """Представляет сущность NotFoundException."""

    pass


async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    """Выполняет операцию app exception handler."""
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
