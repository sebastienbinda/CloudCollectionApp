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
# Description : modele ORM des utilisateurs applicatifs.

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Sequence, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class User(DatabaseModelBase):
    """Represente un utilisateur applicatif rattache a une collection.

    Attributes:
        id (int): Identifiant technique genere par la sequence `s_user`.
        email (str): Adresse email unique de l'utilisateur.
        password_encrypted (str): Mot de passe chiffre.
        creation_date (datetime): Date de creation de l'utilisateur.
        last_connexion_date (Optional[datetime]): Date de derniere connexion.
        collection_file_path (Optional[str]): Chemin du fichier de collection.
        collection_file_description (Optional[dict]): Description structuree du
            fichier de collection stockee en JSONB.
    """

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
