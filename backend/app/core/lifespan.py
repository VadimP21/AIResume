"""Содержит компоненты модуля lifespan."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Выполняет операцию lifespan."""
    logger.info("application_startup")

    yield

    logger.info("application_shutdown")
