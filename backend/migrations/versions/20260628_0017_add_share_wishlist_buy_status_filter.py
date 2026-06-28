#   ____ _                 _  ____      _ _           _   _             ___
# Projet : CloudCollectionApp
# Date de creation : 2026-06-28
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
# Description : ajout du filtre d'achat wishlist par defaut aux partages.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260628_0017"
down_revision: Union[str, None] = "20260627_0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute le filtre d'achat wishlist par defaut des partages.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.add_column(
        "t_collection_share",
        sa.Column(
            "wishlist_buy_status_default_filter",
            sa.String(length=8),
            nullable=False,
            server_default="all",
        ),
        schema=schema_name,
    )
    op.create_check_constraint(
        "ck_t_collection_share_wishlist_buy_status_default_filter",
        "t_collection_share",
        "wishlist_buy_status_default_filter IN ('all', 'yes', 'no')",
        schema=schema_name,
    )


def downgrade() -> None:
    """Supprime le filtre d'achat wishlist par defaut des partages.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_constraint(
        "ck_t_collection_share_wishlist_buy_status_default_filter",
        "t_collection_share",
        schema=schema_name,
        type_="check",
    )
    op.drop_column(
        "t_collection_share",
        "wishlist_buy_status_default_filter",
        schema=schema_name,
    )
