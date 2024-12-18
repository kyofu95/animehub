# type: ignore
# pylint: disable=redefined-outer-name, missing-function-docstring, unsubscriptable-object

import pytest_asyncio
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import clear_mappers, configure_mappers

from app.database.orm import mapper_registry, start_mapper


@pytest_asyncio.fixture
async def in_memory_db():

    # set up sqlite in-memory:
    engine = create_async_engine("sqlite+aiosqlite://")

    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)

@pytest_asyncio.fixture
async def sqlite_sessionfactory(in_memory_db, monkeypatch):

    # replace postgresql special insert with sqlite's
    monkeypatch.setattr("app.database.repositories.anime_repository.pg_insert", insert)

    clear_mappers()
    configure_mappers()

    start_mapper()

    async_session_factory = async_sessionmaker(in_memory_db, expire_on_commit=False)
    yield async_session_factory

    clear_mappers()
