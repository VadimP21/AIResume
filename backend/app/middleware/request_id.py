"""Содержит компоненты модуля request_id."""

from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Представляет сущность RequestIDMiddleware."""

    async def dispatch(
        self,
        request,
        call_next,
    ):
        """Выполняет операцию dispatch."""
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid4()),
        )
        request.state.request_id = request_id

        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response
