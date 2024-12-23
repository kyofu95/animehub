# type: ignore
# pylint: disable=redefined-outer-name, missing-function-docstring, missing-class-docstring, unsubscriptable-object

from app.interface.repository.anime_repository import BaseAnimeRepository
from app.interface.repository.user_repository import BaseUserRepository
from app.interface.uow.base_uow import BaseUnitOfWork


class InMemoryUserRepository(BaseUserRepository):

    def __init__(self):
        self.user_dict = {}

    async def add(self, entity):

        for _, user in self.user_dict.items():
            if user.login == entity.login:
                raise RuntimeError(f"entity with name {entity.login} already exists")

        self.user_dict[entity.id] = entity
        return entity

    async def get_by_id(self, id_):
        return self.user_dict.get(id_)

    async def get_by_login(self, login):
        for _, user in self.user_dict.items():
            if user.login == login:
                return user

        return None

    async def update(self, entity):
        return entity

    async def delete(self, entity):
        del self.user_dict[entity.id]


class InMemoryAnimeRepository(BaseAnimeRepository):
    def __init__(self) -> None:
        self.anime_dict = {}
        self.genres_dict = {}
        self.studios_dict = {}

    async def add(self, entity):

        for _, anime in self.anime_dict.items():
            if anime.name_en == entity.name_en:
                raise RuntimeError(f"entity with name {entity.name_jp} already exists")

        self.anime_dict[entity.id] = entity
        return entity

    async def get_by_id(self, id_):
        return self.anime_dict.get(id_)

    async def get_by_name(self, name):
        for _, anime in self.anime_dict.items():
            if anime.name_en == name:
                return anime
        return None

    async def add_genres(self, genres):
        stored_genres = {g.name for g in self.genres_dict.values()}
        new_genres = {g.name for g in genres}

        not_stored_genres = new_genres.difference(stored_genres)

        for g in genres:
            if g.name in not_stored_genres:
                self.genres_dict[g.id] = g

        processed_genres = []

        for _, genre in self.genres_dict.items():
            if genre.name in new_genres:
                processed_genres.append(genre)

        return processed_genres

    async def get_all_genres(self):
        return list(self.genres_dict.values())

    async def add_studios(self, studios):
        stored_studios = (s.name for s in self.studios_dict.values())
        new_studios = {s.name for s in studios}

        not_stores_studios = new_studios.difference(stored_studios)

        for s in studios:
            if s.name in not_stores_studios:
                self.studios_dict[s.id] = s

        processed_studios = []

        for _, studio in self.studios_dict.items():
            if studio.name in new_studios:
                processed_studios.append(studio)

        return processed_studios

    async def get_all_studios(self):
        return list(self.studios_dict.values())

    async def update(self, entity):
        return entity

    async def delete(self, entity):
        del self.anime_dict[entity.id]


class InMemoryUnitOfWork(BaseUnitOfWork):
    def __init__(self):
        self.anime_repository = InMemoryAnimeRepository()
        self.user_repository = InMemoryUserRepository()

        self.user_repository_impl = self.user_repository
        self.anime_repository_impl = self.anime_repository

    async def __aenter__(self):

        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):

        await self.rollback()

        return False

    async def commit(self):
        pass

    async def rollback(self):
        pass
