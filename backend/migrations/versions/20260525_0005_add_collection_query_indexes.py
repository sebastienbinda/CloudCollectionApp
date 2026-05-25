#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-25
# Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
# Licence : Apache 2.0
#
"""Ajoute les index des requetes de consultation collection."""

from typing import Sequence, Union

from alembic import op


revision: str = "20260525_0005"
down_revision: Union[str, None] = "20260522_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cree les index de consultation de collection utilisateur.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.create_index(
        "ix_t_user_collection_game_id",
        "t_user_collection",
        ["game_id"],
        schema=schema_name,
    )
    op.create_index(
        "ix_t_game_platform",
        "t_game",
        ["platform"],
        schema=schema_name,
    )
    op.create_index(
        "ix_t_game_developer",
        "t_game",
        ["developer"],
        schema=schema_name,
    )


def downgrade() -> None:
    """Supprime les index de consultation de collection utilisateur.

    Args:
        Aucun.

    Returns:
        None: La fonction ne retourne aucune valeur.
    """

    schema_name = op.get_context().opts["schema_name"]
    op.drop_index("ix_t_game_developer", table_name="t_game", schema=schema_name)
    op.drop_index("ix_t_game_platform", table_name="t_game", schema=schema_name)
    op.drop_index(
        "ix_t_user_collection_game_id",
        table_name="t_user_collection",
        schema=schema_name,
    )
