from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware

import structlog


class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request,
        call_next,
    ):

        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid4()),
        )
        request.state.request_id = request_id

        structlog.contextvars.bind_contextvars(
            request_id=request_id
        )


        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response