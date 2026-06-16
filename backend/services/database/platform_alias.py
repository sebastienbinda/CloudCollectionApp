#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-15
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : modele ORM des alias de plateformes de jeu.

from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Sequence, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class PlatformAlias(DatabaseModelBase):
    """Represente un nom alternatif rattache a une plateforme de reference.

    Attributes:
        id (int): Identifiant technique genere par la sequence `s_platform_alias`.
        platform (int): Identifiant de la plateforme de reference.
        name (str): Nom alternatif utilise pour le matching.
        category (Optional[str]): Categorie fonctionnelle de l'alias.
        usage_region (Optional[str]): Zone ou contexte d'usage de l'alias.
        comment (Optional[str]): Commentaire explicatif sur l'alias.
    """

    __tablename__ = "t_platform_alias"
    __table_args__ = (
        UniqueConstraint("platform", "name", name="uq_t_platform_alias_platform_name"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence("s_platform_alias"),
        primary_key=True,
    )
    platform: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("t_platform.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    usage_region: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
