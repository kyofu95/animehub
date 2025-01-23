from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from app.api.api import api_router
from app.core.exceptions import AlreadyExistsError, DatabaseError, NotFoundError
from app.database.orm import start_mapper


@asynccontextmanager
async def lifespan(fastapi: FastAPI) -> AsyncIterator[None]:
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
    async def not_found_exc(request: Request, exc: NotFoundError):
        return JSONResponse(content={"detail": str(exc)}, status_code=status.HTTP_404_NOT_FOUND)

    @fast_app.exception_handler(AlreadyExistsError)
    async def already_exists_exc(request: Request, exc: AlreadyExistsError):
        return JSONResponse(
            content={"detail": str(exc)},
            status_code=status.HTTP_409_CONFLICT,
        )

    @fast_app.exception_handler(DatabaseError)
    async def database_exc(request: Request, exc: DatabaseError):
        return JSONResponse(
            content={"detail": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function sets up the FastAPI instance, includes API routes, and applies
    any necessary application-wide configurations.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    api = FastAPI(lifespan=lifespan)

    api.include_router(api_router)

    install_exception_handlers(api)

    add_pagination(api)

    return api


app = create_app()
"""The main FastAPI application instance."""
