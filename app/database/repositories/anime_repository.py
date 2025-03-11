from dataclasses import asdict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database.orm import anime_table, franchises_table, genres_table, studios_table
from app.entity.anime import Anime, Franchise, Genre, Studio
from app.interface.repository.anime_repository import BaseAnimeRepository


class AnimeSQLRepository(BaseAnimeRepository):
    """
    A SQL Anime repository.
    """

    def __init__(self, async_session: AsyncSession) -> None:
        """
        Constructor.

        Args:
            async_session (AsyncSession): SQLAlchemy async session, typically obtained
            with DI
        """

        self.session = async_session

    async def add(self, entity: Anime) -> Anime:
        """
        Store entity in database.

        Args:
            entity (Anime): entity to persist

        Returns:
            Anime: returns entity
        """

        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)

        return entity

    async def get_by_id(self, id_: UUID) -> Anime | None:
        """
        Get entity by id.

        Args:
            id_ (UUID): entity's id

        Returns:
            Anime | None: return entity if found, otherwise None
        """

        return await self.session.get(Anime, id_)

    async def get_by_name(self, name: str) -> Anime | None:
        """
        Get entity by name.

        Args:
            name (str): entity's name

        Returns:
            Anime | None: return entity if found, otherwise None
        """

        result = await self.session.execute(select(Anime).where(anime_table.c.name_en == name))
        return result.scalar_one_or_none()

    async def update(self, entity: Anime) -> Anime:
        """
        Update an entity.

        Args:
            entity (Anime): entity

        Raises:
            NotFoundError: in case our entity has persistance problems

        Returns:
            Anime: updated entity
        """

        stored_entity = await self.session.get(Anime, entity.id)
        if not stored_entity:
            raise NotFoundError("Entity has not been stored in database, but were marked for update.")

        await self.session.flush()
        await self.session.refresh(entity)

        return entity

    async def delete(self, entity: Anime) -> None:
        """
        Remove entity from database.

        Args:
            entity (Anime): entity to remove
        """

        await self.session.delete(entity)
        await self.session.flush()

    async def add_genres(self, genres: list[Genre]) -> list[Genre]:
        """
        Inserts new genre entities into database.

        This method inserts multiple 'Genre' records into the database.
        If a genre in the list already exists, the operation does nothing
        for that genre and retrieves the existing records.

        Args:
            genres (list[Genre]): list of genres. May contain new or existing genres.

        Returns:
            list[Genre]: list of stored genres
        """

        if not genres:
            return []

        genre_dicts = [asdict(g) for g in genres]

        await self.session.execute(pg_insert(Genre).values(genre_dicts).on_conflict_do_nothing())

        genre_names = [g.name for g in genres]

        select_result = await self.session.execute(select(Genre).where(genres_table.c.name.in_(genre_names)))

        return list(select_result.scalars().all())

    async def get_all_genres(self) -> list[Genre]:
        """
        Get all stored genres in database.

        Returns:
            list[Genre]: list of genres.
        """

        result = await self.session.execute(select(Genre))

        return list(result.scalars().all())

    async def add_studios(self, studios: list[Studio]) -> list[Studio]:
        """
        Inserts new studio entities into database.

        This method inserts multiple 'Studio' records into the database.
        If any studio in the list already exists, the operation does nothing
        for that studio and fetches the existing records.

        Args:
            studios (list[Studio]): list of studios. May contain new or existing studios.

        Returns:
            list[Studio]: list of stored studios
        """

        if not studios:
            return []

        studio_dicts = [asdict(s) for s in studios]

        await self.session.execute(pg_insert(Studio).values(studio_dicts).on_conflict_do_nothing())

        studio_names = [s.name for s in studios]

        select_result = await self.session.execute(select(Studio).where(studios_table.c.name.in_(studio_names)))

        return list(select_result.scalars().all())

    async def get_all_studios(self) -> list[Studio]:
        """
        Get all stored studios in database.

        Returns:
            list[Studio]: list of studios.
        """

        result = await self.session.execute(select(Studio))

        return list(result.scalars().all())

    async def add_franchise(self, franchise: Franchise) -> Franchise:
        """
        Inserts new franchise entity into database.

        If a franchise with the same name already exists, the operation does nothing and fetches the existing record.

        Args:
            franchise (Franchise): The 'Franchise' object to be added to the database.

        Returns:
            Franchise: The 'Franchise' object after it has been successfully added or retrieved.
        """

        franchise_dicts = [asdict(franchise)]
        await self.session.execute(pg_insert(Franchise).values(franchise_dicts).on_conflict_do_nothing())

        select_result = await self.session.execute(select(Franchise).where(franchises_table.c.name == franchise.name))
        return select_result.scalar_one()

    async def get_with_pagination(
        self, include_genres: list[Genre] | None, excluded_genres: list[Genre] | None, skip: int = 0, limit: int = 10
    ) -> list[Anime]:
        """
        Retrieve a paginated list of Anime objects based on included and excluded genres.

        Args:
            include_genres (list[Genre] | None): A list of genres to filter the results to include.
                                                    Only Anime associated with these genres will be retrieved.
            excluded_genres (list[Genre] | None): A list of genres to filter the results to exclude.
                                                    Anime associated with these genres will be omitted.
            skip (int, optional): _description_. The number of records to skip from the beginning. Defaults to 0.
            limit (int, optional): _description_. The maximum number of records to retrieve. Defaults to 10.

        Returns:
            list[Anime]: A list of Anime objects matching the specified criteria.
        """

        stmt = select(Anime)

        if include_genres:
            included_genre_names = [g.name for g in include_genres]
            stmt = stmt.join(Genre, anime_table.c.id == genres_table.c.id).where(
                genres_table.c.name.in_(included_genre_names)
            )

        if excluded_genres:
            excluded_genre_names = [g.name for g in excluded_genres]
            stmt = stmt.join(Genre, anime_table.c.id == genres_table.c.id).where(
                genres_table.c.name.not_in(excluded_genre_names)
            )

        # default sorting by nocase ascending
        stmt = stmt.order_by(func.upper(anime_table.c.name_en).asc())

        result = await self.session.execute(stmt.offset(skip).limit(limit))

        return list(result.scalars().all())
