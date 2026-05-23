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
# Description : modele ORM des plateformes de jeu.

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Sequence, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class Platform(DatabaseModelBase):
    """Represente une plateforme de jeu video du schema de reference.

    Attributes:
        id (int): Identifiant technique genere par la sequence `s_platform`.
        name (str): Nom de la plateforme.
        release_date (Optional[datetime]): Date de sortie de la plateforme.
        manufacturer (Optional[str]): Fabricant de la plateforme.
        description (Optional[dict]): Description structuree stockee en JSONB.
        status (str): Statut fonctionnel de la plateforme.
    """

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
