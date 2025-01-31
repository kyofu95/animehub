from uuid import UUID

from pydantic import BaseModel

from app.entity.watchlist import WatchingStatus

from .anime import BaseAnime


class BaseWatchlistEntry(BaseModel):
    status: WatchingStatus
    num_watched_episodes: int = 0


class WatchlistEntryRequest(BaseWatchlistEntry):
    pass


class WatchlistEntryResponse(BaseWatchlistEntry):
    id: UUID
    anime: BaseAnime
