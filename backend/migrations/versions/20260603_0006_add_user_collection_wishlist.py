#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
#
# Projet : CloudCollectionApp
# Date de creation : 2026-06-03
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute l'indicateur wishlist aux collections utilisateur."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260603_0006"
down_revision: Union[str, None] = "20260525_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute et initialise `t_user_collection.wishlist`.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.add_column(
        "t_user_collection",
        sa.Column("wishlist", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        schema=schema_name,
    )
    op.execute(
        sa.text(
            f'UPDATE "{schema_name}".t_user_collection '
            "SET wishlist = false WHERE wishlist IS NULL"
        )
    )


def downgrade() -> None:
    """Supprime `t_user_collection.wishlist`.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_column("t_user_collection", "wishlist", schema=schema_name)
