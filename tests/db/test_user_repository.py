# type: ignore
# pylint: disable=redefined-outer-name, missing-function-docstring, unsubscriptable-object, missing-class-docstring

from datetime import date
from uuid import uuid4

import pytest

from app.database.uow.sql_uow import SQLUnitOfWork
from app.entity.anime import AiringStatus, Anime, AnimeType
from app.entity.user import User
from app.entity.watchlist import WatchingEntry, WatchingStatus
from app.interface.repository.exception import NotFoundError


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
async def test_user_repository_basic(sqlite_sessionfactory):
    uow = SQLUnitOfWork(sqlite_sessionfactory)

    async with uow:
        user = User(id=uuid4(), login="a", password="123")

        stored_user = await uow.user_repository.add(user)

    async with uow:
        stored_user = await uow.user_repository.get_by_id(user.id)

        assert stored_user.created_at
        assert stored_user.updated_at

        stored_user.login = "b"

        await uow.user_repository.update(stored_user)

    async with uow:
        stored_user = await uow.user_repository.get_by_login("b")
        assert stored_user

        await uow.user_repository.delete(stored_user)

        deleted_user = await uow.user_repository.get_by_login("b")
        assert deleted_user is None


@pytest.mark.asyncio
async def test_user_repository_watchlist(sqlite_sessionfactory):
    uow = SQLUnitOfWork(sqlite_sessionfactory)

    async with uow:
        anime_a = await uow.anime_repository.add(create_anime_a())
        anime_b = await uow.anime_repository.add(create_anime_b())

        user = User(id=uuid4(), login="a", password="123")

        user = await uow.user_repository.add(user)

        watching_a = WatchingEntry(id=uuid4(), status=WatchingStatus.WATCHING, num_watched_episodes=2, anime=anime_a)
        user.watching_list.append(watching_a)

        watching_b = WatchingEntry(id=uuid4(), status=WatchingStatus.PLANNING, num_watched_episodes=0, anime=anime_b)
        user.watching_list.append(watching_b)

        await uow.user_repository.update(user)

    async with uow:
        stored_user = await uow.user_repository.get_by_id(user.id)

        assert len(stored_user.watching_list) == 2

        stored_user.watching_list[0].num_watched_episodes = 3

        await uow.user_repository.update(stored_user)

        assert stored_user.watching_list[0].num_watched_episodes == 3


@pytest.mark.asyncio
async def test_user_update_exc(sqlite_sessionfactory):
    uow = SQLUnitOfWork(sqlite_sessionfactory)

    async with uow:
        with pytest.raises(NotFoundError) as exc_info:

            not_stored_user = User(id=uuid4(), login="a", password="123")

            _ = await uow.user_repository.update(not_stored_user)

    assert exc_info.type is NotFoundError

@pytest.mark.asyncio
async def test_user_uow_rollback(sqlite_sessionfactory):
    class MyException(RuntimeError):
        pass

    uow = SQLUnitOfWork(sqlite_sessionfactory)

    with pytest.raises(MyException):
        async with uow:
            user = User(id=uuid4(), login="123abc", password="123")
            await uow.user_repository.add(user)
            raise MyException()

    async with uow:
        not_stored_user = await uow.user_repository.get_by_login("123abc")
        assert not_stored_user is None
