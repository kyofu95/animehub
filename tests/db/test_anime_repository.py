# type: ignore
# pylint: disable=redefined-outer-name, missing-function-docstring, unsubscriptable-object

from datetime import date
from uuid import uuid4

import pytest

from app.database.uow.sql_uow import SQLUnitOfWork
from app.entity.anime import AiringStatus, Anime, AnimeType, Episode, Franchise, Genre, Studio
from app.interface.repository.exception import NotFoundError


@pytest.mark.asyncio
async def test_anime_repository_basic(sqlite_sessionfactory):
    """
    add/get_by* with basic anime
    """

    genres = [Genre(id=uuid4(), name="Comedy")]

    studios = [Studio(id=uuid4(), name="CloverWorks")]

    anime = Anime(
        id=uuid4(),
        name_en="Bocchi the Rock! Movie",
        type=AnimeType.MOVIE,
        airing_status=AiringStatus.COMPLETE,
        airing_start=date(2024, 6, 7),
        airing_end=date(2024, 8, 9),
        total_number_of_episodes=2,
        genres=genres,
        studios=studios,
    )

    uow = SQLUnitOfWork(sqlite_sessionfactory)

    async with uow:

        stored_anime = await uow.anime_repository.add(anime)

        stored_anime = await uow.anime_repository.get_by_name("Bocchi the Rock! Movie")
        assert stored_anime

        assert anime.id == stored_anime.id
        assert anime.name_en == stored_anime.name_en
        assert anime.genres[0].name == stored_anime.genres[0].name
        assert anime.studios[0].name == stored_anime.studios[0].name

    async with uow:

        stored_anime = await uow.anime_repository.get_by_id(anime.id)
        assert stored_anime

        assert anime.id == stored_anime.id
        assert anime.name_en == stored_anime.name_en
        assert anime.genres[0].name == stored_anime.genres[0].name
        assert anime.studios[0].name == stored_anime.studios[0].name

        await uow.anime_repository.delete(stored_anime)

        stored_anime = await uow.anime_repository.get_by_name("Bocchi the Rock! Movie")
        assert stored_anime is None


@pytest.mark.asyncio
async def test_anime_repository_extended(sqlite_sessionfactory):
    """
    add/delete/update/get_by* repository methods, with extended anime data
    """

    genres = [Genre(id=uuid4(), name="Comedy")]

    studios = [Studio(id=uuid4(), name="Doga Kobo")]

    anime = Anime(
        id=uuid4(),
        name_en="Himouto! Umaru-chan",
        name_jp="干物妹！うまるちゃん",
        type=AnimeType.TV,
        airing_status=AiringStatus.COMPLETE,
        airing_start=date(2015, 7, 9),
        airing_end=date(2015, 9, 24),
        genres=genres,
        studios=studios,
    )

    uow = SQLUnitOfWork(sqlite_sessionfactory)

    async with uow:

        stored_anime = await uow.anime_repository.add(anime)

    async with uow:
        stored_anime = await uow.anime_repository.get_by_name("Himouto! Umaru-chan")
        assert stored_anime

        assert anime.id == stored_anime.id
        assert anime.name_en == stored_anime.name_en
        assert anime.genres[0].name == stored_anime.genres[0].name
        assert anime.studios[0].name == stored_anime.studios[0].name

    async with uow:
        stored_anime = await uow.anime_repository.get_by_id(anime.id)
        assert stored_anime

        assert anime.id == stored_anime.id
        assert anime.name_en == stored_anime.name_en
        assert anime.genres[0].name == stored_anime.genres[0].name
        assert anime.studios[0].name == stored_anime.studios[0].name

    episodes = [
        Episode(id=uuid4(), name="Umaru and Onii-chan", aired_date=date(2015, 7, 9), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru and Ebina-chan", aired_date=date(2015, 7, 16), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru and Her Student", aired_date=date(2015, 7, 23), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru and Her Rival", aired_date=date(2015, 8, 3), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru and Summer Vacation", aired_date=date(2015, 8, 6), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru's Birthday", aired_date=date(2015, 8, 13), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru's Onii-chan", aired_date=date(2015, 8, 20), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru and Christmas and New Year's", aired_date=date(2015, 8, 27), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru and Valentine's", aired_date=date(2015, 9, 3), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru and Now and Once Upon a Time", aired_date=date(2015, 9, 10), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru's Day", aired_date=date(2015, 9, 17), anime_id=anime.id),
        Episode(id=uuid4(), name="Umaru and Everyone", aired_date=date(2015, 9, 24), anime_id=anime.id),
    ]

    franchise = Franchise(id=uuid4(), name="Himouto! Umaru-chan", anime_id=anime.id)

    async with uow:
        stored_anime = await uow.anime_repository.get_by_id(anime.id)
        assert stored_anime

        stored_anime.episodes = episodes
        stored_anime.total_number_of_episodes = 12
        stored_anime.franchise = franchise

        await uow.anime_repository.update(stored_anime)

    async with uow:

        stored_anime = await uow.anime_repository.get_by_name("Himouto! Umaru-chan")
        assert stored_anime

        assert len(stored_anime.episodes) == len(episodes)
        assert stored_anime.total_number_of_episodes == 12
        assert stored_anime.franchise.name == "Himouto! Umaru-chan"

        await uow.anime_repository.delete(stored_anime)

    async with uow:

        stored_anime = await uow.anime_repository.get_by_name("Himouto! Umaru-chan")
        assert stored_anime is None


@pytest.mark.asyncio
async def test_anime_repository_genres(sqlite_sessionfactory):
    """
    add_genres/get_all_genres repository methods
    """

    genres = [
        Genre(id=uuid4(), name="Comedy"),
        Genre(id=uuid4(), name="Horror"),
    ]

    uow = SQLUnitOfWork(sqlite_sessionfactory)

    async with uow:
        stored_genres_a = await uow.anime_repository.add_genres(genres)
        stored_genres_b = await uow.anime_repository.add_genres(genres)

        assert len(stored_genres_a) == len(stored_genres_b)

        all_stored_genres = await uow.anime_repository.get_all_genres()
        assert len(all_stored_genres) == 2


@pytest.mark.asyncio
async def test_anime_repository_studios(sqlite_sessionfactory):
    """
    add_studios/get_all_studios repository methods
    """

    studios = [
        Studio(id=uuid4(), name="aaa"),
        Studio(id=uuid4(), name="bbb"),
    ]

    uow = SQLUnitOfWork(sqlite_sessionfactory)

    async with uow:

        stored_studios_a = await uow.anime_repository.add_studios(studios)
        stored_studios_b = await uow.anime_repository.add_genres(studios)

        assert len(stored_studios_a) == len(stored_studios_b)

        all_stored_studios = await uow.anime_repository.get_all_studios()
        assert len(all_stored_studios) == 2


@pytest.mark.asyncio
async def test_anime_update_exc(sqlite_sessionfactory):
    uow = SQLUnitOfWork(sqlite_sessionfactory)

    async with uow:
        with pytest.raises(Exception) as exc_info:

            not_stored_anime = Anime(
                id=uuid4(),
                name_en="Bocchi the Rock! Movie",
                type=AnimeType.MOVIE,
                airing_status=AiringStatus.COMPLETE,
                airing_start=date(2024, 6, 7),
                airing_end=date(2024, 8, 9),
            )

            _ = await uow.anime_repository.update(not_stored_anime)

    assert exc_info.type is NotFoundError
