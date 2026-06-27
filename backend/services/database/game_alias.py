#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-27
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : modele ORM des alias de jeux video.

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Sequence, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class GameAlias(DatabaseModelBase):
    """Represente un nom alternatif rattache a un jeu de reference.

    Attributes:
        id (int): Identifiant technique genere par la sequence `s_game_alias`.
        game_id (int): Identifiant du jeu conserve.
        name (str): Nom alternatif utilise pour retrouver un ancien doublon.
        creation_date (datetime): Date de creation de l'alias.
    """

    __tablename__ = "t_game_alias"
    __table_args__ = (
        UniqueConstraint("game_id", "name", name="uq_t_game_alias_game_name"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence("s_game_alias"),
        primary_key=True,
    )
    game_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("t_game.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
