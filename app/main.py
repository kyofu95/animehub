from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.api import api_router


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

    yield


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

    return api


app = create_app()
"""The main FastAPI application instance."""
