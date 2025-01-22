from abc import ABC, abstractmethod
from uuid import UUID

from app.entity.anime import Anime, Franchise, Genre, Studio

from .base_repository import BaseRepository


class BaseAnimeRepository(BaseRepository[Anime], ABC):
    """
    Base anime repository class.
    """

    @abstractmethod
    async def add(self, entity: Anime) -> Anime:
        """Store entity. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id_: UUID) -> Anime | None:
        """Get entity by id. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> Anime | None:
        """Get entity by name. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def add_genres(self, genres: list[Genre]) -> list[Genre]:
        """Create genre entities. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def get_all_genres(self) -> list[Genre]:
        """Get all genre entities. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def add_studios(self, studios: list[Studio]) -> list[Studio]:
        """Create studios entities. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def get_all_studios(self) -> list[Studio]:
        """Get all studio entities. Abstract method."""

        raise NotImplementedError
    
    @abstractmethod
    async def add_franchise(self, franchise: Franchise) -> Franchise:
        """Create franchise entity. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: Anime) -> Anime:
        """Update entity. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: Anime) -> None:
        """Remove entity. Abstract method."""

        raise NotImplementedError

    @abstractmethod
    async def get_with_pagination(
        self, include_genres: list[Genre] | None, excluded_genres: list[Genre] | None, skip: int = 0, limit: int = 10
    ) -> list[Anime]:
        """Query anime entities with optional genre filters."""

        raise NotImplementedError
