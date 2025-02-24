import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from asgi_correlation_id import CorrelationIdFilter, CorrelationIdMiddleware, correlation_id
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from redis.exceptions import RedisError

from app.api.api import api_router
from app.core.config import common_settings
from app.core.exceptions import AlreadyExistsError, DatabaseError, HashingError, NotFoundError
from app.database.orm import start_mapper


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """
    Define the application's lifespan for startup and shutdown events.

    This function is used to manage application-level lifecycle events, such as
    initializing resources on startup or cleaning up resources during shutdown.

    Args:
        fastapi (FastAPI): The FastAPI application instance.

    Yields:
        None: Indicates no additional setup or teardown logic is required.
    """

    start_mapper()

    yield


def init_logger() -> None:
    """
    Initialize and configure the application logger.
    """

    logger = logging.getLogger("")

    formatter = logging.Formatter(
        "%(asctime)s [%(processName)s: %(process)d] [%(levelname)s] [%(correlation_id)s] %(name)s: %(message)s"
    )

    cid_filter = CorrelationIdFilter(uuid_length=32)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.addFilter(cid_filter)

    logger.addHandler(console)

    if common_settings.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def install_exception_handlers(fast_app: FastAPI) -> None:
    """
    Install custom exception handlers for the FastAPI application.
    This function registers exception handlers for specific application-level errors.
    These handlers capture exceptions raised during the request lifecycle and return
    appropriate HTTP responses with error messages.

    Args:
        fast_app (FastAPI): The FastAPI application instance.
    """

    @fast_app.exception_handler(NotFoundError)
    async def not_found_exc(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(content={"detail": str(exc)}, status_code=status.HTTP_404_NOT_FOUND)

    @fast_app.exception_handler(AlreadyExistsError)
    async def already_exists_exc(_: Request, exc: AlreadyExistsError) -> JSONResponse:
        return JSONResponse(
            content={"detail": str(exc)},
            status_code=status.HTTP_409_CONFLICT,
        )

    @fast_app.exception_handler(DatabaseError)
    async def database_exc(_: Request, exc: DatabaseError) -> JSONResponse:
        return JSONResponse(
            content={"detail": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"X-Request-ID": correlation_id.get() or ""},
        )

    @fast_app.exception_handler(HashingError)
    async def hashing_exc(_: Request, exc: HashingError) -> JSONResponse:
        return JSONResponse(
            content={"detail": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={"X-Request-ID": correlation_id.get() or ""},
        )

    @fast_app.exception_handler(RedisError)
    async def redis_exc(_: Request, exc: RedisError) -> JSONResponse:
        return JSONResponse(
            content={"detail": str(exc)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            headers={"X-Request-ID": correlation_id.get() or ""},
        )


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function sets up the FastAPI instance, includes API routes, and applies
    any necessary application-wide configurations.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    init_logger()

    logger = logging.getLogger(__name__)
    logger.info("Application startup")

    if common_settings.debug:
        logger.debug("Debug active")

    docs_url = None
    openapi_url = None

    if common_settings.docs:
        docs_url = "/docs"
        openapi_url = "/openapi.json"

    api = FastAPI(
        debug=common_settings.debug,
        title="AnimeHub",
        version="0.9",
        openapi_url=openapi_url,
        docs_url=docs_url,
        redoc_url=None,
        lifespan=lifespan,
    )

    api.include_router(api_router)

    install_exception_handlers(api)

    add_pagination(api)
    # supress fastapi_pagination warning
    disable_installed_extensions_check()

    api.add_middleware(CorrelationIdMiddleware)

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["X-Requested-With", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    return api


app = create_app()
"""The main FastAPI application instance."""
