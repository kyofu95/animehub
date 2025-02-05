from uuid import UUID

from pydantic import BaseModel, Field

from app.entity.watchlist import WatchingStatus

from .anime import BaseAnime


class BaseWatchlistEntry(BaseModel):
    """Base schema representing a watchlist entry for an anime."""

    status: WatchingStatus = Field(
        title="Watching status",
        description="Current watching status of the anime (e.g., Watching, Completed, Dropped).",
    )
    num_watched_episodes: int = Field(
        0, title="Watched episodes", description="Number of episodes watched by the user."
    )


class WatchlistEntryRequest(BaseWatchlistEntry):
    """Schema for adding or updating a watchlist entry request."""


class WatchlistEntryResponse(BaseWatchlistEntry):
    """Response schema for a watchlist entry, including the associated anime and unique identifier."""

    id: UUID = Field(title="Watchlist entry ID", description="Unique identifier for the watchlist entry.")
    anime: BaseAnime = Field(title="Anime", description="The anime associated with this watchlist entry.")
