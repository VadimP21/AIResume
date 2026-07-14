"""Содержит компоненты модуля lifespan."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Выполняет операцию lifespan."""
    logger.info("application_startup")

    yield

    logger.info("application_shutdown")
