from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum, unique
from uuid import UUID


@unique
class AnimeType(StrEnum):
    """
    An anime type.

    Values:
        TV: TV (seasonal) anime
        MOVIE: Movie anime
    """

    TV = "TV"
    MOVIE = "MOVIE"


@unique
class AiringStatus(StrEnum):
    """
    An anime airing status.

    Values:
        AIRING: Airing is ongoing
        COMPLETE: Completed airing, can be applied to movies
    """

    AIRING = "AIRING"
    COMPLETE = "COMPLETE"


@dataclass
class Genre:
    """
    A genre entity.
    """

    id: UUID
    name: str


@dataclass
class Studio:
    """
    A studio entity.
    """

    id: UUID
    name: str


@dataclass
class Franchise:
    """
    A franchise entity.
    """

    id: UUID
    name: str

    #optional attribute
    anime_id: UUID

    anime: list[Anime] = field(default_factory=lambda: [])


@dataclass
class Episode:
    """
    An anime episode entity. Contains data of individual episode.
    """

    id: UUID
    name: str
    aired_date: date | None

    #optional attributes
    anime_id: UUID


@dataclass
class Anime:
    """
    Represents an anime entity within the application.
    """

    id: UUID
    name_en: str
    type: AnimeType
    airing_status: AiringStatus
    airing_start: date
    name_jp: str | None = None

    total_number_of_episodes: int | None = None

    airing_end: date | None = None
    description: str | None = None
    rating: str | None = None

    episodes: list[Episode] = field(default_factory=lambda:[])
    genres: list[Genre] = field(default_factory=lambda:[])
    studios: list[Studio] = field(default_factory=lambda:[])
    franchise: Franchise | None = None
