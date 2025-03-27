from abc import ABC, abstractmethod
from uuid import UUID

from app.entity.user import User

from .base_repository import BaseRepository


class BaseUserRepository(BaseRepository[User], ABC):
    """Base user repository class."""

    @abstractmethod
    async def add(self, entity: User) -> User:
        """Store entity. Abstract method."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id_: UUID) -> User | None:
        """Get entity by id. Abstract method."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_login(self, login: str) -> User | None:
        """Get entity by login. Abstract method."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: User) -> User:
        """Update entity. Abstract method."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity: User) -> None:
        """Remove entity. Abstract method."""
        raise NotImplementedError
