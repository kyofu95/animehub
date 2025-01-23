from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database.orm import user_table
from app.entity.user import User
from app.interface.repository.user_repository import BaseUserRepository


class UserSQLRepository(BaseUserRepository):
    """
    A SQL User repository.
    """

    def __init__(self, async_session: AsyncSession) -> None:
        """
        Constructor.

        Args:
            async_session (AsyncSession): SQLAlchemy async session, typically obtained
            with DI
        """

        self.session = async_session

    async def add(self, entity: User) -> User:
        """
        Store entity in database.

        Args:
            entity (User): entity to persist

        Returns:
            User: returns entity
        """

        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)

        return entity

    async def get_by_id(self, id_: UUID) -> User | None:
        """
        Get entity by id.

        Args:
            id_ (UUID): entity's id

        Returns:
            User | None: return entity if found, otherwise None
        """

        return await self.session.get(User, id_)

    async def get_by_login(self, login: str) -> User | None:
        """
        Get entity by login.

        Args:
            login (str): entity's login

        Returns:
            User | None: return entity if found, otherwise None
        """

        result = await self.session.execute(select(User).where(user_table.c.login == login))
        return result.scalar_one_or_none()

    async def update(self, entity: User) -> User:
        """Update an entity.

        Args:
            entity (Anime): enitity

        Raises:
            NotFoundError: in case our entity has persistance problems

        Returns:
            Anime: updated entity
        """

        stored_entity = await self.session.get(User, entity.id)
        if not stored_entity:
            raise NotFoundError("Entity has not beed stored in database, but were marked for update.")

        await self.session.flush()
        await self.session.refresh(entity)

        return entity

    async def delete(self, entity: User) -> None:
        """Remove entity from database.

        Args:
            entity (User): entity to remove
        """

        await self.session.delete(entity)
        await self.session.flush()
