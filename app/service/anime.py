from datetime import date
from uuid import UUID, uuid4

from app.entity.anime import AiringStatus, Anime, Episode, AnimeType, Franchise, Genre, Studio
from app.interface.uow.base_uow import BaseUnitOfWork


class AnimeAlreadyExistsError(Exception):
    """
    Attempting to create an anime that already exists.
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
