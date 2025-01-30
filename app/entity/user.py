from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .watchlist import WatchingEntry


@dataclass
class User:
    """
    Represents a user entity within the application.
    """

    id: UUID
    login: str
    password: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    active: bool = True
    admin: bool = False

    watching_list: list[WatchingEntry] = field(default_factory=list)
