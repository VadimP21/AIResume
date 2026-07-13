import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
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
