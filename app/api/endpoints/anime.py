from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from app.entity.anime import Episode, Franchise, Genre, Studio

from .schemes.anime import BaseAnimeResponse, DetailedAnimeRequest, DetailedAnimeResponse
from .utils.di_deps import AnimeServiceDep

router = APIRouter(prefix="/anime", tags=["Anime"])


@router.post("/", response_model=BaseAnimeResponse, status_code=status.HTTP_201_CREATED)
async def create_anime(anime_request: DetailedAnimeRequest, anime_service: AnimeServiceDep) -> BaseAnimeResponse:
    """
    Create a new anime entry.

    This endpoint allows creating a new anime along with its associated episodes, genres, studios,
    and franchise.

    Args:
        anime_request (DetailedAnimeRequest): he input data for the new anime, including its details,
            episodes, genres, studios, and franchise information.
        anime_service (AnimeServiceDep): The AnimeService dependency for handling anime creation.

    Raises:
        HTTPException: If an anime with the given English name already exists.

    Returns:
        BaseAnimeResponse: A response object containing the details of the created anime.
    """

    existing_anime = await anime_service.get_by_name(anime_request.name_en)
    if existing_anime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Anime with name '{anime_request.name_en}' already exists"
        )

    anime_id = uuid4()

    episodes: list[Episode] | None = None
    if anime_request.episodes:
        episodes = list()
        for ep in anime_request.episodes:
            a = Episode(id=uuid4(), name=ep.name, aired_date=ep.aired_date, anime_id=anime_id)
            episodes.append(a)

    genres: list[Genre] | None = None
    if anime_request.genres:
        genres = list()
        for genre in anime_request.genres:
            g = Genre(id=uuid4(), name=genre.name)
            genres.append(g)

    studios: list[Studio] | None = None
    if anime_request.studios:
        studios = list()
        for studio in anime_request.studios:
            s = Studio(id=uuid4(), name=studio.name)
            studios.append(s)

    franchise: Franchise | None = None
    if anime_request.franchise:
        franchise = Franchise(id=uuid4(), name=anime_request.franchise.name, anime_id=anime_id)

    anime = await anime_service.create(
        english_name=anime_request.name_en,
        type_=anime_request.type,
        airing_status=anime_request.airing_status,
        airing_start=anime_request.airing_start,
        airing_end=anime_request.airing_end,
        japanese_name=anime_request.name_jp,
        total_number_of_episodes=anime_request.total_number_of_episodes,
        description=anime_request.description,
        rating=anime_request.rating,
        episodes=episodes,
        genres=genres,
        studios=studios,
        franchise=franchise,
        id_=anime_id,
    )

    return BaseAnimeResponse.model_validate(anime, from_attributes=True)


@router.get("/{anime_id}", response_model=BaseAnimeResponse, status_code=status.HTTP_200_OK)
async def get_anime_by_id(anime_id: UUID, anime_service: AnimeServiceDep) -> BaseAnimeResponse:
    """
    Retrieve an anime by its ID.

    This endpoint fetches the basic details of an anime identified by its unique ID.
    If no anime with the given ID is found, a 404 Not Found error is raised.

    Args:
        anime_id (UUID): The unique ID of the anime to retrieve.
        anime_service (AnimeServiceDep): The AnimeService dependency for fetching anime details.

    Raises:
        HTTPException: If no anime with the given ID exists.

    Returns:
        BaseAnimeResponse: A response object containing the details of the anime.
    """

    anime = await anime_service.get_by_id(anime_id)
    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Anime with id '{anime_id}' doesn't exist.")

    return BaseAnimeResponse.model_validate(anime, from_attributes=True)


@router.get("/{anime_id}/detail", response_model=DetailedAnimeResponse, status_code=status.HTTP_200_OK)
async def get_anime_details_by_id(anime_id: UUID, anime_service: AnimeServiceDep) -> DetailedAnimeResponse:
    """
    Retrieve detailed information about an anime by its ID.

    This endpoint fetches comprehensive details of an anime, including associated episodes, genres,
    studios, and franchise, identified by its unique ID. If no anime with the given ID is found, a
    404 Not Found error is raised.

    Args:
        anime_id (UUID): The unique ID of the anime to retrieve information for.
        anime_service (AnimeServiceDep): The AnimeService dependency for fetching anime information.

    Raises:
        HTTPException: If no anime with the given ID exists.

    Returns:
        DetailedAnimeResponse: A response object containing the detailed information of the anime.
    """

    anime = await anime_service.get_by_id(anime_id)
    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Anime with id '{anime_id}' doesn't exist.")

    return DetailedAnimeResponse.model_validate(anime, from_attributes=True)
