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
# Description : modele ORM des studios de jeux video.

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Sequence, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class Studio(DatabaseModelBase):
    """Represente un studio createur ou editeur de jeux video.

    Attributes:
        id (int): Identifiant technique genere par la sequence `s_studio`.
        name (str): Nom unique du studio.
        country (Optional[str]): Pays du studio.
        city (Optional[str]): Ville du studio.
        creation_date (Optional[datetime]): Date de creation du studio.
        status (str): Statut fonctionnel du studio.
    """

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
