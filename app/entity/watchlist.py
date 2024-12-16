from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique
from uuid import UUID

from .anime import Anime


@unique
class WatchingStatus(Enum):
    """
    Status of anime added to watchlist.

    Values:
        WATCHING: Watching right now
        COMPLETED: User finished watching
        DROPPPED: User decided not to continue watching
        PLANNING: On wishlist
    """

    WATCHING = "WATCHING"
    COMPLETED = "COMPLETED"
    DROPPPED = "DROPPED"
    PLANNING = "PLANNING"


@dataclass
class WatchingEntry:
    """
    A watching table. Represents the watching status of an episodic animation or movie for a user.
    """

    id: UUID
    status: WatchingStatus

    anime: Anime

    num_watched_episodes: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
