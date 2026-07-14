"""Содержит компоненты модуля security."""

from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Представляет сущность SecurityHeadersMiddleware."""

    async def dispatch(self, request, call_next):
        """Выполняет операцию dispatch."""
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin"

        return response
