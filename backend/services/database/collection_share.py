#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-06-23
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : modele ORM des partages temporaires de collection.

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column

from .database_model_base import DatabaseModelBase


class CollectionShare(DatabaseModelBase):
    """Represente un partage temporaire cree par un proprietaire de collection.

    Attributes:
        id (int): Identifiant technique genere par `s_collection_share`.
        owner_user_id (int): Identifiant du proprietaire de la collection.
        created_at (datetime): Date de creation du partage.
        expires_at (datetime): Date d'expiration du partage.
        revoked_at (Optional[datetime]): Date de revocation ou absence.
        recipient (Optional[str]): Destinataire lisible du partage.
        allow_collection (bool): Autorisation de consulter la collection.
        allow_wishlist (bool): Autorisation de consulter la liste de souhaits.
        allow_prices (bool): Autorisation de consulter les prix.
        wishlist_buy_status_default_filter (str): Filtre d'achat wishlist par defaut.
    """

    __tablename__ = "t_collection_share"
    __table_args__ = (
        CheckConstraint(
            "expires_at > created_at",
            name="ck_t_collection_share_expiration",
        ),
        CheckConstraint(
            "wishlist_buy_status_default_filter IN ('all', 'yes', 'no')",
            name="ck_t_collection_share_wishlist_buy_status_default_filter",
        ),
        Index("ix_t_collection_share_owner_user_id", "owner_user_id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Sequence("s_collection_share"),
        primary_key=True,
    )
    owner_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("t_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    recipient: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    allow_collection: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allow_wishlist: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allow_prices: Mapped[bool] = mapped_column(Boolean, nullable=False)
    wishlist_buy_status_default_filter: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        default="all",
    )
