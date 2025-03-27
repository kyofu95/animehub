from datetime import datetime, timezone

from sqlalchemy import UUID, Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

import app.entity.anime as anime_entity
import app.entity.user as user_entity
import app.entity.watchlist as watchlist_entity

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)

mapper_registry = registry(metadata=metadata)

genres_table = Table(
    "genres", mapper_registry.metadata, Column("id", UUID, primary_key=True), Column("name", String, unique=True),
)
studios_table = Table(
    "studios", mapper_registry.metadata, Column("id", UUID, primary_key=True), Column("name", String, unique=True),
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
    Column("type", Enum(anime_entity.AnimeType)),
    Column("airing_status", Enum(anime_entity.AiringStatus)),
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
    Column("status", Enum(watchlist_entity.WatchingStatus)),
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
    Column("login", String, unique=True),
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
    """Initialize and configure the SQLAlchemy ORM mapper registry."""
    mapper_registry.map_imperatively(anime_entity.Genre, genres_table)
    mapper_registry.map_imperatively(anime_entity.Studio, studios_table)

    mapper_registry.map_imperatively(
        anime_entity.Franchise,
        franchises_table,
        properties={"anime": relationship(anime_entity.Anime, back_populates="franchise", uselist=True)},
    )

    mapper_registry.map_imperatively(
        anime_entity.Episode,
        episodes_table,
        properties={"anime": relationship(anime_entity.Anime, back_populates="episodes")},
    )

    mapper_registry.map_imperatively(
        anime_entity.Anime,
        anime_table,
        properties={
            "episodes": relationship(
                anime_entity.Episode,
                back_populates="anime",
                uselist=True,
                lazy="selectin",
                cascade="all, delete-orphan",
                order_by=episodes_table.c.aired_date,
            ),
            "genres": relationship(anime_entity.Genre, secondary=anime_genre_association_table, lazy="selectin"),
            "studios": relationship(anime_entity.Studio, secondary=anime_studio_association_table, lazy="selectin"),
            "franchise": relationship(anime_entity.Franchise, back_populates="anime", uselist=False, lazy="selectin"),
        },
    )

    mapper_registry.map_imperatively(
        watchlist_entity.WatchingEntry,
        watching_entry_table,
        properties={
            "user": relationship(user_entity.User, back_populates="watching_list", uselist=False),
            "anime": relationship(anime_entity.Anime, uselist=False, backref="Anime", lazy="selectin"),
        },
    )

    mapper_registry.map_imperatively(
        user_entity.User,
        user_table,
        properties={
            "watching_list": relationship(
                watchlist_entity.WatchingEntry, back_populates="user", uselist=True, lazy="selectin",
            ),
        },
    )
