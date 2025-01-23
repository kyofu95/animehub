from datetime import date
from typing import Any
from uuid import UUID, uuid4

from app.entity.anime import AiringStatus, Anime, AnimeType, Episode, Franchise, Genre, Studio
from app.interface.uow.base_uow import BaseUnitOfWork


class AnimeAlreadyExistsError(Exception):
    """
    Attempting to create an anime that already exists.
    """


class AnimeNotExistsError(Exception):
    """ "
    Exception raised when a requested anime does not exist.
    """


class AnimeService:
    """
    Service layer for handling operations related to anime data.

    Provides methods for creating, retrieving, and updating anime data.
    """

    def __init__(self, uow: BaseUnitOfWork) -> None:
        self.uow = uow
        """
        Constructor.

        Args:
            uow (BaseUnitOfWork): An instance of BaseUnitOfWork for managing sessions and user repository.
        """

    async def create(
        self,
        english_name: str,
        type_: AnimeType,
        airing_status: AiringStatus,
        airing_start: date,
        japanese_name: str | None = None,
        total_number_of_episodes: int | None = None,
        airing_end: date | None = None,
        description: str | None = None,
        rating: str | None = None,
        episodes: list[Episode] | None = None,
        genres: list[Genre] | None = None,
        studios: list[Studio] | None = None,
        franchise: Franchise | None = None,
        id_: UUID | None = None,
    ) -> Anime:
        """
        Creates a new anime instance.

        Args:
            english_name (str): The English name of the anime.
            type_ (AnimeType): The type of the anime (e.g., TV, movie, OVA).
            airing_status (AiringStatus): The current airing status of the anime.
            airing_start (date): The start date of the anime's airing schedule.
            japanese_name (str | None): The Japanese name of the anime. Defaults to None if not provided.
            total_number_of_episodes (int | None): The total number of episodes in the anime.
                Defaults to None if not provided.
            airing_end (date | None): The end date of the anime's airing schedule. Defaults to None if not provided.
            description (str | None): A brief description of the anime. Defaults to None if not provided.
            rating (str | None): The rating of the anime (e.g., PG, R). Defaults to None if not provided.
            episodes (list[AnimeEpisode] | None): A list of episode instances for the anime.
                Defaults to None if not provided.
            genres (list[Genre] | None): A list of genre instances for the anime. Defaults to None if not provided.
            studios (list[Studio] | None): A list of studio instances associated with the anime.
                Defaults to None if not provided.
            franchise (Franchise | None): The franchise that the anime belongs to. Defaults to None if not provided.
            id_ (UUID | None): Anime id. Defaults to None if not provided and will be generated on place.

        Raises:
            AnimeAlreadyExistsError: If an anime with the same login already exists.

        Returns:
            Anime | None: The newly created anime instance.
        """

        async with self.uow as uow:

            existing_anime = await uow.anime_repository.get_by_name(english_name)
            if existing_anime:
                raise AnimeAlreadyExistsError("Trying to create an anome with existing name")

            if not id_:
                id_ = uuid4()

            processed_genres: list[Genre] = []
            if genres:
                processed_genres = await uow.anime_repository.add_genres(genres)

            processed_studios: list[Studio] = []
            if studios:
                processed_studios = await uow.anime_repository.add_studios(studios)

            if episodes is None:
                episodes = []

            anime = Anime(
                id=id_,
                name_en=english_name,
                name_jp=japanese_name,
                type=type_,
                total_number_of_episodes=total_number_of_episodes,
                airing_status=airing_status,
                airing_start=airing_start,
                airing_end=airing_end,
                description=description,
                rating=rating,
                episodes=episodes,
                genres=processed_genres,
                studios=processed_studios,
                franchise=franchise,
            )

            return await uow.anime_repository.add(anime)

    async def get_by_id(self, id_: UUID) -> Anime | None:
        """
        Retrieves an anime instance by its id.

        Args:
            id_ (UUID): The id of the anime to retrieve.

        Returns:
            Anime | None: The retrieved anime instance, or None if not found.
        """

        async with self.uow as uow:
            return await uow.anime_repository.get_by_id(id_)

    async def get_by_name(self, name: str) -> Anime | None:
        """
        Retrieves an anime instance by its name.

        Args:
            name (str): The name of the anime to retrieve.

        Returns:
            Anime | None: The retrieved anime instance, or None if not found.
        """

        async with self.uow as uow:
            return await uow.anime_repository.get_by_name(name)

    async def update(self, id_: UUID, update_dict: dict[str, Any]) -> Anime:
        """
        Updates an existing anime with the provided ID.

        Args:
            id_ (UUID): The id of the anime to update.
            update_dict (dict[str, Any]):  A dictionary containing the updated values for the anime.

        Raises:
            AnimeNotExistsError: If an anime with given ID doesn't exists.

        Returns:
            Anime: The updated anime instance.
        """

        async with self.uow as uow:
            anime = await uow.anime_repository.get_by_id(id_)
            if not anime:
                raise AnimeNotExistsError(f"Anime with id '{id_}' does not exist.")

            for k, v in update_dict.items():
                # skip complex fields for now
                if k in ["episodes", "genres", "studios", "franchise"]:
                    continue
                existing_value = anime.__dict__[k]
                if v != existing_value:
                    anime.__dict__[k] = v

            # process 'episodes', 'genres', 'studios' and 'franchise' separately
            if update_dict["episodes"]:
                anime.episodes = []
                new_episodes = update_dict["episodes"]
                for e in new_episodes:
                    anime.episodes.append(Episode(uuid4(), e.name, e.aired_date, anime_id=anime.id))

            if update_dict["genres"]:
                genres: list[dict[str, str]] = update_dict["genres"]
                new_genres = [Genre(id=uuid4(), name=g["name"]) for g in genres]
                anime.genres = await uow.anime_repository.add_genres(new_genres)

            if update_dict["studios"]:
                studios: list[dict[str, str]] = update_dict["studios"]
                new_studios = [Studio(id=uuid4(), name=s["name"]) for s in studios]
                anime.studios = await uow.anime_repository.add_studios(new_studios)

            if update_dict["franchise"]:
                anime.franchise = await uow.anime_repository.add_franchise(
                    Franchise(id=uuid4(), name=update_dict["franchise"].name, anime_id=anime.id)
                )

            return await uow.anime_repository.update(anime)

    async def get_with_pagination(
        self, include_genres: list[str] | None, excluded_genres: list[str] | None, skip: int = 0, limit: int = 10
    ) -> list[Anime]:
        """
        Retrieve a paginated list of Anime objects based on included and excluded genre names.

        Args:
            include_genres (list[str] | None): A list of genre names to include in the results.
                                                Only Anime associated with these genres will be retrieved.
                                                If `None`, no inclusion filter is applied.
            excluded_genres (list[str] | None): A list of genre names to exclude from the results.
                                                Anime associated with these genres will be omitted.
                                                If `None`, no exclusion filter is applied.
            skip (int, optional): The number of records to skip from the beginning of the results. Defaults to 0.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 10.

        Returns:
            list[Anime]: _description_
        """

        async with self.uow as uow:
            all_genres = await uow.anime_repository.get_all_genres()

            all_genres_dict = {g.name: g for g in all_genres}

            processed_include_genres: list[Genre] | None = None
            if include_genres:
                processed_include_genres = []
                for genre_name in include_genres:
                    genre = all_genres_dict.get(genre_name)
                    if genre:
                        processed_include_genres.append(genre)

            processed_exclude_genres: list[Genre] | None = None
            if excluded_genres:
                processed_exclude_genres = []
                for genre_name in excluded_genres:
                    genre = all_genres_dict.get(genre_name)
                    if genre:
                        processed_exclude_genres.append(genre)

            anime = await uow.anime_repository.get_with_pagination(
                include_genres=processed_include_genres,
                excluded_genres=processed_exclude_genres,
                skip=skip,
                limit=limit,
            )

            return anime
