from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.entity.anime import AiringStatus, AnimeType


class BaseAnime(BaseModel):
    """Base schema representing an anime entity with core attributes."""

    name_en: str = Field(title="English name", description="The English title of the anime.")
    name_jp: str | None = Field(None, title="Japanese Name", description="The original Japanese title of the anime.")
    type: AnimeType = Field(title="Anime Type", description="The type of anime, such as TV series, movie, OVA, etc.")
    total_number_of_episodes: int | None = Field(
        None, title="Total Episodes", description="Total number of episodes in the anime, if known.",
    )
    airing_status: AiringStatus = Field(
        title="Airing Status", description="Current airing status of the anime (e.g., ongoing, completed).",
    )
    airing_start: date = Field(title="Airing Start Date", description="The date when the anime started airing.")
    airing_end: date | None = Field(
        None, title="Airing End Date", description="The date when the anime ended airing, if applicable.",
    )


class BaseAnimeResponse(BaseAnime):
    """Response schema for anime with a unique identifier."""

    id: UUID = Field(title="Anime ID", description="Unique identifier for the anime.")


class Episode(BaseModel):
    """Schema representing an episode of an anime."""

    name: str = Field(title="Episode Name", description="The title of the episode.")
    aired_date: date | None = Field(None, title="Aired Date", description="The date when the episode aired, if known.")


class GenreRequest(BaseModel):
    """Schema representing a genre request."""

    name: str = Field(title="Genre Name", description="The name of the genre.")


class StudioRequest(BaseModel):
    """Schema representing a studio request."""

    name: str = Field(title="Studio Name", description="The name of the animation studio.")


class FranchiseRequest(BaseModel):
    """Schema representing a franchise request."""

    name: str = Field(title="Franchise Name", description="The name of the franchise the anime belongs to.")


class DetailedAnime(BaseAnime):
    """Schema for detailed anime information, including episodes, genres, studios, and franchise details."""

    description: str | None = Field(None, title="Description", description="A brief summary or synopsis of the anime.")
    rating: str | None = Field(None, title="Rating", description="The age rating or user rating of the anime.")

    episodes: list[Episode] | None = Field(None, title="Episodes", description="A list of episodes in the anime.")
    genres: list[GenreRequest] | None = Field(
        None, title="Genres", description="A list of genres associated with the anime.",
    )
    studios: list[StudioRequest] | None = Field(
        None, title="Studios", description="A list of animation studios involved in the anime.",
    )

    franchise: FranchiseRequest | None = Field(
        None, title="Franchise", description="The franchise this anime belongs to, if applicable.",
    )


class DetailedAnimeRequest(DetailedAnime):
    """Request schema for creating or updating a detailed anime record."""


class DetailedAnimeResponse(DetailedAnime):
    """Response schema for detailed anime information, including a unique identifier."""

    id: UUID = Field(title="Anime ID", description="Unique identifier for the anime.")
