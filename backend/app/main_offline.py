from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_offline import FastAPIOffline
from slowapi.middleware import SlowAPIMiddleware
from starlette.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.app_logging import setup_logging
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
)
from app.core.lifespan import lifespan
from app.core.rate_limit import limiter
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import SecurityHeadersMiddleware

setup_logging()

app = FastAPIOffline(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.airesume.com",
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "status": "ok",
    }
