"""TransitOps application entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.api import api_router
from src.core.config import get_settings
from src.core.database import close_mongo_connection, connect_to_mongo
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging
from src.middleware.auth_context import AuthContextMiddleware
from src.middleware.request_context import RequestContextMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application startup and shutdown resources."""

    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting TransitOps application")

    await connect_to_mongo()
    try:
        yield
    finally:
        await close_mongo_connection()
        logger.info("TransitOps application stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
    )

    app.add_middleware(AuthContextMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    return app


app = create_app()
