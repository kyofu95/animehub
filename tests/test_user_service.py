# type: ignore
# pylint: disable=redefined-outer-name, missing-function-docstring, missing-class-docstring
# pylint: disable=unsubscriptable-object, wrong-import-order

from datetime import date
from uuid import uuid4

import pytest

from app.core.exceptions import AlreadyExistsError
from app.core.security import Hasher
from app.entity.anime import AiringStatus, Anime, AnimeType
from app.entity.watchlist import WatchingStatus
from app.service.user import UserService
from in_memory_deps import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_user_service():
    uow = InMemoryUnitOfWork()
    service = UserService(uow)

    created_user = await service.create("aaa", "b")
    assert created_user

    with pytest.raises(AlreadyExistsError) as exc_info:
        await service.create("aaa", "b")
    assert exc_info.type is AlreadyExistsError

    assert len(uow.user_repository_impl.user_dict) == 1

    stored_user = await service.get_by_id(created_user.id)
    assert stored_user

    not_existing_user = await service.get_by_id(uuid4())
    assert not_existing_user is None

    assert created_user.login == stored_user.login

    not_existing_user = await service.get_by_login_auth("wrong_login", "password")
    assert not_existing_user is None

    wrong_password_hash = Hasher.hash("wrong_password")

    user_with_wrong_password = await service.get_by_login_auth("aaa", wrong_password_hash)
    assert user_with_wrong_password is None


def create_anime_a():
    return Anime(
        id=uuid4(),
        name_en="AAA",
        airing_status=AiringStatus.COMPLETE,
        airing_start=date(2000, 1, 1),
        airing_end=date(2001, 1, 1),
        type=AnimeType.TV,
        total_number_of_episodes=12,
    )


def create_anime_b():
    return Anime(
        id=uuid4(),
        name_en="BBB",
        airing_status=AiringStatus.COMPLETE,
        airing_start=date(2000, 1, 1),
        airing_end=date(2001, 1, 1),
        type=AnimeType.TV,
        total_number_of_episodes=12,
    )


@pytest.mark.asyncio
async def test_user_service_watching_entry():
    uow = InMemoryUnitOfWork()
    service = UserService(uow)

    user = await service.create("aaa", "b")
    assert user

    async with uow:
        anime_a = await uow.anime_repository.add(create_anime_a())
        anime_b = await uow.anime_repository.add(create_anime_b())

    await service.create_watching_entry(
        status=WatchingStatus.WATCHING, num_watched_episodes=1, user=user, anime=anime_a
    )
    assert len(user.watching_list) == 1

    await service.create_watching_entry(
        status=WatchingStatus.WATCHING, num_watched_episodes=1, user=user, anime=anime_b
    )
    assert len(user.watching_list) == 2

    with pytest.raises(AlreadyExistsError) as exc_info:
        await service.create_watching_entry(
            status=WatchingStatus.WATCHING, num_watched_episodes=1, user=user, anime=anime_a
        )
    assert exc_info.type is AlreadyExistsError
    assert len(user.watching_list) == 2
