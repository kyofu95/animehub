from datetime import datetime, timezone

from sqlalchemy import UUID, Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

import app.entity.anime as AnimeEntity
import app.entity.user as UserEntity
import app.entity.watchlist as WatchlistEntity

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

mapper_registry = registry(metadata=metadata)

genres_table = Table(
    "genres", mapper_registry.metadata, Column("id", UUID, primary_key=True), Column("name", String, unique=True)
)
studios_table = Table(
    "studios", mapper_registry.metadata, Column("id", UUID, primary_key=True), Column("name", String, unique=True)
)
franchises_table = Table(
    "franchises",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("name", String, unique=True),
    Column("anime_id", UUID, ForeignKey("anime.id")),
)

episodes_table = Table(
    "episodes",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("name", String),
    Column("aired_date", Date),
    Column("anime_id", UUID, ForeignKey("anime.id")),
)

anime_genre_association_table = Table(
    "anime_genre",
    mapper_registry.metadata,
    Column("anime_id", ForeignKey("anime.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)

anime_studio_association_table = Table(
    "anime_studio",
    mapper_registry.metadata,
    Column("anime_id", ForeignKey("anime.id"), primary_key=True),
    Column("studio_id", ForeignKey("studios.id"), primary_key=True),
)

anime_table = Table(
    "anime",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("name_en", String, unique=True),
    Column("type", Enum(AnimeEntity.AnimeType)),
    Column("airing_status", Enum(AnimeEntity.AiringStatus)),
    Column("airing_start", Date),
    Column("airing_end", Date, nullable=True),
    Column("name_jp", String, nullable=True),
    Column("total_number_of_episodes", Integer, nullable=True),
    Column("description", String, nullable=True),
    Column("rating", String, nullable=True),
)

watching_entry_table = Table(
    "watching_entry",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("status", Enum(WatchlistEntity.WatchingStatus)),
    Column("num_watched_episodes", Integer),
    Column("created_at", DateTime(timezone=True), nullable=True, default=datetime.now(timezone.utc)),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=True,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    ),
    Column("anime_id", UUID, ForeignKey("anime.id")),
    Column("user_id", UUID, ForeignKey("user.id")),
)

user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("login", String),
    Column("password", String),
    Column("created_at", DateTime(timezone=True), nullable=True, default=datetime.now(timezone.utc)),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=True,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    ),
    Column("active", Boolean, default=True),
    Column("admin", Boolean, default=False),
)


def start_mapper() -> None:
    """
    Initialize and configure the SQLAlchemy ORM mapper registry.
    """

    mapper_registry.map_imperatively(AnimeEntity.Genre, genres_table)
    mapper_registry.map_imperatively(AnimeEntity.Studio, studios_table)

    mapper_registry.map_imperatively(
        AnimeEntity.Franchise,
        franchises_table,
        properties={"anime": relationship(AnimeEntity.Anime, back_populates="franchise", uselist=True)},
    )

    mapper_registry.map_imperatively(
        AnimeEntity.Episode,
        episodes_table,
        properties={"anime": relationship(AnimeEntity.Anime, back_populates="episodes")},
    )

    mapper_registry.map_imperatively(
        AnimeEntity.Anime,
        anime_table,
        properties={
            "episodes": relationship(AnimeEntity.Episode, back_populates="anime", uselist=True, lazy="selectin"),
            "genres": relationship(AnimeEntity.Genre, secondary=anime_genre_association_table, lazy="selectin"),
            "studios": relationship(AnimeEntity.Studio, secondary=anime_studio_association_table, lazy="selectin"),
            "franchise": relationship(AnimeEntity.Franchise, back_populates="anime", uselist=False, lazy="selectin"),
        },
    )

    mapper_registry.map_imperatively(
        WatchlistEntity.WatchingEntry,
        watching_entry_table,
        properties={
            "user": relationship(UserEntity.User, back_populates="watching_list", uselist=False),
            "anime": relationship(AnimeEntity.Anime, uselist=False, backref="Anime"),
        },
    )

    mapper_registry.map_imperatively(
        UserEntity.User,
        user_table,
        properties={
            "watching_list": relationship(
                WatchlistEntity.WatchingEntry, back_populates="user", uselist=True, lazy="selectin"
            )
        },
    )
