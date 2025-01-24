# type: ignore
# pylint: disable=redefined-outer-name, missing-function-docstring, missing-class-docstring
# pylint: disable=unsubscriptable-object, wrong-import-order

from datetime import date
from uuid import uuid4

import pytest

from app.core.exceptions import AlreadyExistsError
from app.service.anime import AiringStatus, AnimeService, AnimeType, Episode, Genre, Studio
from in_memory_deps import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_anime_service():
    uow = InMemoryUnitOfWork()
    service = AnimeService(uow)

    created_anime = await service.create("a", AnimeType.MOVIE, AiringStatus.COMPLETE, date(2002, 1, 1))
    assert created_anime

    with pytest.raises(AlreadyExistsError) as exc_info:
        already_existing_anime = await service.create("a", AnimeType.MOVIE, AiringStatus.COMPLETE, date(2002, 1, 1))
        assert already_existing_anime is None
    assert exc_info.type is AlreadyExistsError

    existing_anime = await service.get_by_id(created_anime.id)
    assert existing_anime


@pytest.mark.asyncio
async def test_anime_service_ex():
    uow = InMemoryUnitOfWork()
    service = AnimeService(uow)

    anime_id = uuid4()

    episodes = [
        Episode(id=uuid4(), name="111", aired_date=date(2002, 1, 1), anime_id=anime_id),
        Episode(id=uuid4(), name="222", aired_date=date(2002, 1, 15), anime_id=anime_id),
    ]

    genres = [Genre(id=uuid4(), name="AAA")]

    studios = [Studio(id=uuid4(), name="BBB")]

    created_anime = await service.create(
        english_name="a",
        type_=AnimeType.TV,
        airing_status=AiringStatus.COMPLETE,
        airing_start=date(2002, 1, 1),
        airing_end=date(2002, 1, 15),
        description="aaa",
        episodes=episodes,
        genres=genres,
        studios=studios,
        id_=anime_id,
    )
    assert created_anime
    assert len(created_anime.episodes) == 2
