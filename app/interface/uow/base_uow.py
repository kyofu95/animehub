from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from app.interface.repository.anime_repository import BaseAnimeRepository
from app.interface.repository.user_repository import BaseUserRepository


class BaseUnitOfWork(ABC):
    """
    Base Unit-of-Work class. Provides asynchronous context manager interface.

    Attributes:
        anime_repository (BaseAnimeRepository): Repository for anime-related operations.
        user_repository (BaseUserRepository): Repository for user-related operations.
    """

    anime_repository: BaseAnimeRepository
    user_repository: BaseUserRepository

    async def __aenter__(self) -> BaseUnitOfWork:
        """Enter the asynchronous context manager."""

        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, exc_tb: TracebackType | None
    ) -> bool | None:
        """Exit the asynchronous context manager."""

        await self.rollback()
        return False

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction. Abstract method."""

        raise NotImplementedError
