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
# Description : modele ORM des jeux video.

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Sequence, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class Game(DatabaseModelBase):
    """Represente un jeu video reference dans une plateforme.

    Attributes:
        id (int): Identifiant technique genere par la sequence `s_game`.
        name (str): Nom du jeu.
        release_date (Optional[datetime]): Date de sortie du jeu.
        developper (Optional[int]): Identifiant du studio de developpement.
        editor (Optional[int]): Identifiant du studio editeur.
        platform (int): Identifiant de la plateforme du jeu.
        description (Optional[dict]): Description structuree stockee en JSONB.
    """

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
