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


class ValidationException(AppException):
    """Представляет ошибку валидации бизнес-данных."""

    pass


async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    """Выполняет операцию app exception handler."""
    logger.error(
        "application_error",
        message=exc.message,
        request_id=getattr(request.state, "request_id", None),
    )

    status_code = (
        status.HTTP_422_UNPROCESSABLE_CONTENT
        if isinstance(exc, ValidationException)
        else status.HTTP_404_NOT_FOUND
        if isinstance(exc, NotFoundException)
        else status.HTTP_400_BAD_REQUEST
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.message,
        },
    )
