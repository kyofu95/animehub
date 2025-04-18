from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.database.database import async_session_factory
from app.database.redis import get_redis
from app.database.uow.sql_uow import SQLUnitOfWork
from app.service.anime import AnimeService
from app.service.user import UserService


def get_user_service() -> UserService:
    """
    Dependency injection function that provides an instance of UserService.

    Returns:
        UserService: An instance of the UserService.
    """
    uow = SQLUnitOfWork(async_session_factory)
    return UserService(uow)


def get_anime_service() -> AnimeService:
    """
    Dependency injection function that provides an instance of AnimeService.

    Returns:
        AnimeService: An instance of the AnimeService.
    """
    uow = SQLUnitOfWork(async_session_factory)
    return AnimeService(uow)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
"""Dependency for providing an instance of UserService."""

AnimeServiceDep = Annotated[AnimeService, Depends(get_anime_service)]
"""Dependency for providing an instance of AnimeService."""

RedisDep = Annotated[Redis, Depends(get_redis)]
"""Dependency for providing an instance of Redis."""
