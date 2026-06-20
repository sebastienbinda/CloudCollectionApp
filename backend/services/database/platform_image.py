#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-18
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : modele ORM des images proposees pour les plateformes.

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Sequence,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class PlatformImage(DatabaseModelBase):
    """Represente une image proposee pour une plateforme du referentiel.

    Attributes:
        id (int): Identifiant technique genere par la sequence `s_platform_image`.
        platform (int): Identifiant de la plateforme associee.
        path (str): Chemin absolu du fichier image stocke sur disque.
        file_size_bytes (int): Taille du fichier image stocke en octets.
        type (str): Type fonctionnel de l'image, `MAIN` ou `OTHER`.
        status (str): Statut de validation, `WAITING_VALIDATION` ou `ACCEPTED`.
        user_id (int): Identifiant de l'utilisateur ayant propose l'image.
        creation_date (datetime): Date de creation de la proposition.
    """

    __tablename__ = "t_platform_image"
    __table_args__ = (
        CheckConstraint("type IN ('MAIN', 'OTHER')", name="ck_t_platform_image_type"),
        CheckConstraint("file_size_bytes >= 0", name="ck_t_platform_image_file_size_bytes"),
        CheckConstraint(
            "status IN ('WAITING_VALIDATION', 'ACCEPTED')",
            name="ck_t_platform_image_status",
        ),
        Index("ix_t_platform_image_platform", "platform"),
        Index("ix_t_platform_image_status", "status"),
        Index("ix_t_platform_image_user_id", "user_id"),
        Index(
            "uq_t_platform_image_single_main",
            "platform",
            unique=True,
            postgresql_where=text("type = 'MAIN'"),
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence("s_platform_image"),
        primary_key=True,
    )
    platform: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("t_platform.id"),
        nullable=False,
    )
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False, default="OTHER")
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="WAITING_VALIDATION",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("t_user.id"),
        nullable=False,
    )
    creation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
