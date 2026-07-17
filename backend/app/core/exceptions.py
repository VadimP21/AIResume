"""Содержит компоненты модуля exceptions."""

from typing import cast

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


class ServiceUnavailableException(AppException):
    """Представляет временную недоступность внешнего сервиса или зависимости."""

    pass


async def app_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Выполняет операцию app exception handler."""
    app_exception = cast(AppException, exc)
    logger.error(
        "application_error",
        message=app_exception.message,
        request_id=getattr(request.state, "request_id", None),
    )

    status_code = (
        status.HTTP_503_SERVICE_UNAVAILABLE
        if isinstance(app_exception, ServiceUnavailableException)
        else status.HTTP_422_UNPROCESSABLE_CONTENT
        if isinstance(app_exception, ValidationException)
        else status.HTTP_404_NOT_FOUND
        if isinstance(app_exception, NotFoundException)
        else status.HTTP_400_BAD_REQUEST
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": app_exception.message,
        },
    )
