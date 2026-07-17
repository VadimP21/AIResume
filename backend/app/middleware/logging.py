"""Содержит компоненты модуля logging."""

import time
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Представляет сущность LoggingMiddleware."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Выполняет операцию dispatch."""
        start = time.time()

        response = await call_next(request)

        process_time = time.time() - start

        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time,
            request_id=request.state.request_id,
        )

        return response
