#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-12
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : modeles ORM SQLAlchemy du schema relationnel initial.

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Sequence, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DatabaseModelBase(DeclarativeBase):
    """Classe de base declarative pour les modeles ORM PostgreSQL."""


class SchemaVersion(DatabaseModelBase):
    """Represente la version applicative inscrite apres initialisation SQL."""

    __tablename__ = "t_schema_version"

    version: Mapped[str] = mapped_column(String(5), primary_key=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    update_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Platform(DatabaseModelBase):
    """Represente une plateforme de jeu video du schema de reference."""

    __tablename__ = "t_platform"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence("s_platform"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    release_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    description: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)


class Studio(DatabaseModelBase):
    """Represente un studio createur ou editeur de jeux video."""

    __tablename__ = "t_studio"
    __table_args__ = (UniqueConstraint("name", name="uq_t_studio_name"),)

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence("s_studio"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    creation_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)


class User(DatabaseModelBase):
    """Represente un utilisateur applicatif rattache a une collection."""

    __tablename__ = "t_user"
    __table_args__ = (UniqueConstraint("email", name="uq_t_user_email"),)

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence("s_user"),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String(256), nullable=False)
    password_encrypted: Mapped[str] = mapped_column(String(512), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_connexion_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    collection_file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    collection_file_description: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class Game(DatabaseModelBase):
    """Represente un jeu video reference dans une plateforme."""

    __tablename__ = "t_game"
    __table_args__ = (UniqueConstraint("name", "platform", name="uq_t_game_name_platform"),)

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence("s_game"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    release_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    developper: Mapped[Optional[int]] = mapped_column(ForeignKey("t_studio.id"), nullable=True)
    editor: Mapped[Optional[int]] = mapped_column(ForeignKey("t_studio.id"), nullable=True)
    platform: Mapped[int] = mapped_column(ForeignKey("t_platform.id"), nullable=False)
    description: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class UserCollection(DatabaseModelBase):
    """Represente l'association entre un utilisateur et un jeu possede."""

    __tablename__ = "t_user_collection"

    user_id: Mapped[int] = mapped_column(ForeignKey("t_user.id"), primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("t_game.id"), primary_key=True)
    game_additional_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
