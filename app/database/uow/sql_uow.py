import logging
from types import TracebackType

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import common_settings
from app.core.exceptions import BaseError, DatabaseError
from app.database.repositories.anime_repository import AnimeSQLRepository
from app.database.repositories.user_repository import UserSQLRepository
from app.interface.uow.base_uow import BaseUnitOfWork


class SQLUnitOfWork(BaseUnitOfWork):
    """
    Implementation of Unit-of-Work using SQLAlchemy.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """
        Constructor.

        Args:
            session_factory (async_sessionmaker[AsyncSession]): Factory for creating SQLAlchemy sessions.
        """

        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> BaseUnitOfWork:
        """Enter the asynchronous context manager."""

        self.session = self.session_factory()
        self.anime_repository = AnimeSQLRepository(self.session)
        self.user_repository = UserSQLRepository(self.session)
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, exc_tb: TracebackType | None
    ) -> bool | None:
        """Exit the asynchronous context manager."""

        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

        if self.session:
            await self.session.close()

        # do not omit logic exceptions
        if isinstance(exc_value, BaseError):
            return False

        if isinstance(exc_value, SQLAlchemyError):
            if common_settings.debug:
                logging.exception("A sqlalchemy exception has been occured and trapped inside UoW")
            raise DatabaseError from exc_value

        return False

    async def commit(self) -> None:
        """Commit the current transaction."""

        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""

        if self.session:
            await self.session.rollback()
