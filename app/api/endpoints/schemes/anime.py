from datetime import date
from uuid import UUID

from pydantic import BaseModel

from app.entity.anime import AiringStatus, AnimeType


class BaseAnime(BaseModel):
    name_en: str
    name_jp: str | None = None
    type: AnimeType
    total_number_of_episodes: int | None = None
    airing_status: AiringStatus
    airing_start: date
    airing_end: date | None = None


class BaseAnimeResponse(BaseAnime):
    id: UUID


class Episode(BaseModel):
    name: str
    aired_date: date | None


class GenreRequest(BaseModel):
    name: str


class StudioRequest(BaseModel):
    name: str


class FranchiseRequest(BaseModel):
    name: str


class DetailedAnime(BaseAnime):
    description: str | None = None
    rating: str | None = None

    episodes: list[Episode] | None = None
    genres: list[GenreRequest] | None = None
    studios: list[StudioRequest] | None = None

    franchise: FranchiseRequest | None = None


class DetailedAnimeRequest(DetailedAnime):
    pass


class DetailedAnimeResponse(DetailedAnime):
    id: UUID
